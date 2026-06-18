# File Research: sources/virtualization/nvme-cli/scripts/meson-vcs-tag.sh

Meson helper for deriving a version tag from git.

Key elements:
- Requires source directory and fallback version arguments.
- Changes into the source directory before running git to avoid dirty-tree false positives with `--git-dir`.
- If `.git` exists, runs `git describe --abbrev=7 --dirty=+` and strips a leading `v`.
- Falls back to the provided fallback string when no `.git` metadata exists.

Role:
- Supplies build-time version strings for Meson builds, including tarball builds without git metadata.
