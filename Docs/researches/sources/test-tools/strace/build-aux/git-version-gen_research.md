<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/build-aux/git-version-gen -->
# sources/test-tools/strace/build-aux/git-version-gen

Purpose: GNU-derived shell script that prints strace's version string from `.tarball-version`, Git tags, or fallback values.

Important options: `--prefix`, `--fallback`, `--help`, and `--version`. It reads a tarball version file when valid; otherwise uses `git describe` matching prefixed tags, normalizes older two-part describe output, rewrites separators to package-version-friendly dots, strips the tag prefix, and appends `-dirty` when Git-derived and the worktree differs from HEAD.

Control flow: argument parser accepts one tarball file and optional tag sed script. Version fallback order is tarball, Git describe, `UNKNOWN`, or explicit fallback when Git is unavailable.

State and persistence: reads Git metadata and may refresh the Git index with `git update-index --refresh`; writes stdout only.

Dependencies and integration: called by configure/Autotools version logic and `.version` generation.

Risks: dirty detection can be affected by filesystem metadata and index state. Tag prefix/sed normalization must match release tag policy. Test signals: run in clean tagged checkout, dirty checkout, no-tag checkout, and unpacked tarball with `.tarball-version`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/build-aux/git-version-gen -->
