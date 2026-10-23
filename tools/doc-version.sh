#!/usr/bin/env sh
set -eu

out_dir=".quarto/generated"
yaml_out="$out_dir/doc-version.yml"
tex_out="$out_dir/pdf-version.tex"

mkdir -p "$out_dir"

status="Draft"

format_draft_version() {
  describe="$1"

  case "$describe" in
    *-*-g*)
      dirty_suffix=""
      if [ "${describe%-dirty}" != "$describe" ]; then
        dirty_suffix="-dirty"
        describe="${describe%-dirty}"
      fi

      commit="${describe##*-}"
      tag_and_count="${describe%-"$commit"}"
      count="${tag_and_count##*-}"
      tag="${tag_and_count%-"$count"}"
      tag="${tag%-}"

      if [ "$count" != "0" ] || [ -n "$dirty_suffix" ]; then
        printf 'post-%s %s%s\n' "$tag" "$commit" "$dirty_suffix"
        return
      fi
      ;;
  esac

  printf '%s\n' "$describe"
}

if [ "${1:-}" = "--format-draft-version" ]; then
  format_draft_version "$2"
  exit 0
fi

version="$(format_draft_version "$(git describe --tags --dirty --always --long)")"

if tag="$(git describe --tags --exact-match HEAD 2>/dev/null)" && git diff-index --quiet HEAD --; then
  version="$tag"
  status="Release"
fi

yaml_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

tex_escape() {
  printf '%s' "$1" | sed \
    -e 's/\\/\\textbackslash{}/g' \
    -e 's/{/\\{/g' \
    -e 's/}/\\}/g' \
    -e 's/#/\\#/g' \
    -e 's/\$/\\$/g' \
    -e 's/%/\\%/g' \
    -e 's/&/\\&/g' \
    -e 's/_/\\_/g' \
    -e 's/\^/\\textasciicircum{}/g' \
    -e 's/~/\\textasciitilde{}/g'
}

escaped_yaml_version="$(yaml_escape "$version")"
escaped_yaml_status="$(yaml_escape "$status")"
escaped_tex_version="$(tex_escape "$version")"
escaped_tex_status="$(tex_escape "$status")"

{
  printf 'doc-version: "%s"\n' "$escaped_yaml_version"
  printf 'doc-status: "%s"\n' "$escaped_yaml_status"
} > "$yaml_out"

{
  printf '\\newcommand{\\DocVersion}{%s}\n' "$escaped_tex_version"
  printf '\\newcommand{\\DocStatus}{%s}\n' "$escaped_tex_status"
} > "$tex_out"
