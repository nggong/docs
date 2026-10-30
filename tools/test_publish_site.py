#!/usr/bin/env python3
"""Local tests for preservation, cleanup, build identity, and artifact boundaries."""
import importlib.util
import io
import os
import subprocess
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location("publisher", Path(__file__).with_name("publish-site.py"))
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def archive(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as output:
        for name, content in entries.items():
            output.writestr(name, content)
    return stream.getvalue()


class PublishingTests(unittest.TestCase):
    def test_concurrent_previews_production_update_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            incoming = root / "incoming"
            site.mkdir()
            incoming.mkdir()
            (incoming / "index.html").write_text("production")
            publisher.replace_site(site, incoming, "production")
            for number in ("1", "2"):
                (incoming / "index.html").write_text(number)
                publisher.replace_site(site, incoming, number)
            (site / "old.html").write_text("obsolete")
            (incoming / "index.html").write_text("new production")
            publisher.replace_site(site, incoming, "production")
            self.assertFalse((site / "old.html").exists())
            self.assertEqual((site / "pr/1/index.html").read_text(), "1")
            self.assertEqual((site / "pr/2/index.html").read_text(), "2")
            state = {"production": 10, "1": 11, "2": 12}
            publisher.prune_previews(site, state, {"2"})
            self.assertFalse((site / "pr/1").exists())
            self.assertNotIn("1", state)
            self.assertEqual((site / "pr/2/index.html").read_text(), "2")
            self.assertEqual((site / "index.html").read_text(), "new production")

    def test_storage_branch_and_deployment_retry(self):
        # Exercise real Git commits, clone/fetch, and pushes against a local remote.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            original_command = publisher.command
            current_run = {"id": 10, "conclusion": "success",
                           "path": ".github/workflows/publish.yml",
                           "repository": {"full_name": "nggong/docs"},
                           "event": "push", "head_sha": "abc", "head_branch": "main"}
            open_prs = []

            def fake_api(path):
                if "/artifacts?" in path:
                    return {"artifacts": [{"id": 99, "name": "documentation-site", "expired": False}]}
                if "/actions/runs/" in path:
                    return current_run
                if "/git/ref/" in path:
                    return {"object": {"sha": "abc"}}
                raise AssertionError(path)

            def local_command(*args, **kwargs):
                if args[:4] == ("git", "remote", "add", "origin"):
                    args = (*args[:4], str(remote))
                if args[0] == "gh":
                    return subprocess.CompletedProcess(args, 0, archive({
                        "index.html": str(current_run["id"]), "_pdf/docs/sdp.pdf": b"pdf"}))
                return original_command(*args, **kwargs)

            def publish(run_id):
                runner = root / f"runner-{len(list(root.glob('runner-*')))}"
                runner.mkdir()
                previous_cwd = Path.cwd()
                try:
                    os.chdir(runner)
                    with patch.dict(os.environ, {
                        "GITHUB_REPOSITORY": "nggong/docs", "GH_TOKEN": "test-token",
                        "BUILD_RUN_ID": run_id, "GITHUB_STEP_SUMMARY": str(runner / "summary"),
                        "GITHUB_OUTPUT": str(runner / "output"),
                    }), patch.object(publisher, "command", side_effect=local_command), \
                            patch.object(publisher, "api", side_effect=fake_api), \
                            patch.object(publisher, "pages", return_value=open_prs):
                        publisher.main()
                    self.assertEqual((runner / "output").read_text(), "ready=true\n")
                    return runner / "pages-store/site"
                finally:
                    os.chdir(previous_cwd)

            site = publish("10")
            self.assertEqual((site / "index.html").read_text(), "10")
            # Retry stored content after a failed Pages deployment without an artifact download.
            site = publish("")
            self.assertEqual((site / "index.html").read_text(), "10")
            current_run.update(id=11, event="pull_request", pull_requests=[{"number": 1}])
            open_prs.append({"number": 1, "head": {"sha": "abc", "repo": {"full_name": "nggong/docs"}}})
            site = publish("11")
            self.assertEqual((site / "pr/1/_pdf/docs/sdp.pdf").read_bytes(), b"pdf")
            current_run.update(id=9)
            site = publish("9")  # Same SHA, but an older build must not replace run 11.
            self.assertEqual((site / "pr/1/index.html").read_text(), "11")
            open_prs.clear()
            site = publish("")
            self.assertFalse((site / "pr/1").exists())
            self.assertEqual((site / "index.html").read_text(), "10")

    def test_pdf_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            publisher.extract_site(archive({"index.html": "home", "_pdf/docs/sdp.pdf": b"pdf"}), root)
            self.assertEqual((root / "_pdf/docs/sdp.pdf").read_bytes(), b"pdf")

    def test_reject_unsafe_entries_before_extracting(self):
        for name in ("../escape", "/absolute", ".git/config", "a/../../escape", "a\\escape", "pr/2/index.html"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaises(ValueError):
                    publisher.extract_site(archive({"index.html": "home", name: "bad"}), root, production=True)
                self.assertEqual(list(root.iterdir()), [])

    def test_reject_symlink(self):
        entry = zipfile.ZipInfo("link")
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                publisher.extract_site(archive({"index.html": "home", entry: "../outside"}), Path(directory))

    def test_reject_missing_home_page(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                publisher.extract_site(archive({"other.html": "other"}), Path(directory))

    def test_pr_identity_and_current_commit(self):
        run = {"conclusion": "success", "path": ".github/workflows/publish.yml",
               "repository": {"full_name": "nggong/docs"}, "event": "pull_request",
               "head_sha": "abc", "pull_requests": [{"number": 1}]}
        pr = {"number": 1, "head": {"sha": "abc", "repo": {"full_name": "nggong/docs"}}}
        self.assertEqual(publisher.select_target("nggong/docs", run, [pr]), "1")
        self.assertIsNone(publisher.select_target("nggong/docs", run, []))  # closed
        pr["head"]["sha"] = "newer"
        self.assertIsNone(publisher.select_target("nggong/docs", run, [pr]))
        pr["head"]["sha"] = "abc"
        pr["head"]["repo"]["full_name"] = "fork/docs"
        self.assertIsNone(publisher.select_target("nggong/docs", run, [pr]))

    def test_production_commit_and_workflow_validation(self):
        run = {"conclusion": "success", "path": ".github/workflows/publish.yml",
               "repository": {"full_name": "nggong/docs"}, "event": "push",
               "head_sha": "abc", "head_branch": "main"}
        with patch.object(publisher, "api", return_value={"object": {"sha": "abc"}}):
            self.assertEqual(publisher.select_target("nggong/docs", run, []), "production")
        with patch.object(publisher, "api", return_value={"object": {"sha": "newer"}}):
            self.assertIsNone(publisher.select_target("nggong/docs", run, []))
        run["path"] = ".github/workflows/other.yml"
        self.assertIsNone(publisher.select_target("nggong/docs", run, []))


if __name__ == "__main__":
    unittest.main()
