#!/usr/bin/env python3
"""Maintain generated Pages output. Run only from trusted main-branch code."""
import base64
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import zipfile

STORE = Path("pages-store")
BRANCH = "gh-pages"
SITE = STORE / "site"


def command(*args, cwd=None, capture=False, check=True):
    return subprocess.run(args, cwd=cwd, check=check,
                          stdout=subprocess.PIPE if capture else None)


def api(path):
    return json.loads(command("gh", "api", path, capture=True).stdout)


def pages(path):
    result = command("gh", "api", "--paginate", "--slurp", path, capture=True)
    return [item for page in json.loads(result.stdout) for item in page]


def extract_site(data, destination, production=False):
    """Accept regular static files only; never let an artifact escape its directory."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if sum(info.file_size for info in archive.infolist()) > 512 * 1024 * 1024:
            raise ValueError("Site artifact exceeds 512 MiB")
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if (path.is_absolute() or ".." in path.parts or "\\" in info.filename
                    or ".git" in path.parts or not path.parts
                    or (production and path.parts[0] == "pr")
                    or stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                raise ValueError(f"Unsafe artifact entry: {info.filename!r}")
        if "index.html" not in archive.namelist():
            raise ValueError("Site artifact has no root index.html")
        archive.extractall(destination)


def select_target(repo, run, open_prs):
    """Verify build identity and current source SHA using trusted GitHub API data."""
    if (run["conclusion"] != "success"
            or run["path"] != ".github/workflows/publish.yml"
            or run["repository"]["full_name"] != repo):
        return None
    if run["event"] == "pull_request":
        # Forks are deliberately excluded from automatic publication.
        for pr in open_prs:
            if (pr["head"]["repo"] and pr["head"]["repo"]["full_name"] == repo
                    and pr["head"]["sha"] == run["head_sha"]
                    and any(p["number"] == pr["number"] for p in run["pull_requests"])):
                return str(pr["number"])
        return None
    if run["event"] not in ("push", "workflow_dispatch"):
        return None
    branch = run["head_branch"]
    if branch == "main":
        ref = api(f"repos/{repo}/git/ref/heads/main")["object"]
    elif run["event"] == "push" and branch.startswith("v"):
        from urllib.parse import quote
        ref = api(f"repos/{repo}/git/ref/tags/{quote(branch, safe='')}")["object"]
        while ref["type"] == "tag":
            ref = api(f"repos/{repo}/git/tags/{ref['sha']}")["object"]
    else:
        return None
    return "production" if ref["sha"] == run["head_sha"] else None


def prune_previews(site, state, active):
    previews = site / "pr"
    if previews.exists():
        for path in previews.iterdir():
            if path.name not in active:
                shutil.rmtree(path)
                state.pop(path.name, None)


def replace_site(site, incoming, target):
    if target == "production":
        for path in site.iterdir():
            if path.name != "pr":
                shutil.rmtree(path) if path.is_dir() else path.unlink()
        shutil.copytree(incoming, site, dirs_exist_ok=True)
    else:
        destination = site / "pr" / target
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(incoming, destination)


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    # Use environment-based Git configuration so credentials never enter command logs.
    auth = base64.b64encode(("x-access-token:" + os.environ["GH_TOKEN"]).encode()).decode()
    os.environ.update(GIT_CONFIG_COUNT="1",
                      GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                      GIT_CONFIG_VALUE_0="AUTHORIZATION: basic " + auth)
    command("git", "init", str(STORE))
    command("git", "remote", "add", "origin", f"https://github.com/{repo}.git", cwd=STORE)
    exists = command("git", "ls-remote", "--exit-code", "origin", f"refs/heads/{BRANCH}",
                     cwd=STORE, capture=True, check=False)
    if exists.returncode == 0:
        command("git", "fetch", "--depth=1", "origin", BRANCH, cwd=STORE)
        command("git", "checkout", "-B", BRANCH, "FETCH_HEAD", cwd=STORE)
    elif exists.returncode == 2:
        command("git", "checkout", "--orphan", BRANCH, cwd=STORE)
    else:
        raise RuntimeError("Cannot read Pages storage branch")
    SITE.mkdir(exist_ok=True)
    state_path = STORE / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    open_prs = pages(f"repos/{repo}/pulls?state=open&base=main&per_page=100")
    prune_previews(SITE, state, {str(pr["number"]) for pr in open_prs})

    run_id = os.environ.get("BUILD_RUN_ID", "")
    if run_id:
        if not run_id.isdecimal():
            raise ValueError("Build run ID must be numeric")
        run = api(f"repos/{repo}/actions/runs/{run_id}")
        target = select_target(repo, run, open_prs)
        if target and int(run_id) >= state.get(target, 0):
            artifacts = api(f"repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100")["artifacts"]
            artifact = next(a for a in artifacts if a["name"] == "documentation-site" and not a["expired"])
            data = command("gh", "api", f"repos/{repo}/actions/artifacts/{artifact['id']}/zip",
                           capture=True).stdout
            # Validate before removing any previously published output.
            incoming = STORE / "incoming"
            extract_site(data, incoming, production=target == "production")
            replace_site(SITE, incoming, target)
            shutil.rmtree(incoming)
            state[target] = int(run_id)
            url = "https://nggong.github.io/docs/"
            if target != "production":
                url += f"pr/{target}/"
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
                summary.write(f"Content prepared for deployment: [{url}]({url})\n\nBuild: `{run['head_sha']}`\n")
        else:
            print("Skip ineligible, stale, closed, or fork PR build.")

    state_path.write_text(json.dumps(state, indent=2) + "\n")
    command("git", "config", "user.name", "github-actions[bot]", cwd=STORE)
    command("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", cwd=STORE)
    command("git", "add", "--all", cwd=STORE)
    changed = command("git", "diff", "--cached", "--quiet", cwd=STORE, check=False)
    if changed.returncode == 1:
        command("git", "commit", "-m", "Update published documentation", cwd=STORE)
        command("git", "push", "origin", BRANCH, cwd=STORE)
    elif changed.returncode != 0:
        raise RuntimeError("Cannot inspect Pages storage changes")
    # A first PR build may arrive before the initial production build.
    ready = (SITE / "index.html").is_file()
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"ready={str(ready).lower()}\n")


if __name__ == "__main__":
    main()
