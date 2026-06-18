
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/smart-make -->
# Research: sources/sync-backup/rsync/packaging/smart-make

## Purpose
`packaging/smart-make` is a convenience build wrapper that prepares the source, reruns configure only when `configure.sh` changes, executes `config.status`, builds `make all`, and optionally runs `make check`.

## Important APIs, Types, and Functions
This shell script has no functions. It uses `packaging/prep-auto-dir` to decide whether to build in `build/` with `srcdir=..` or in the source directory with `srcdir=.`.

## Control Flow
The script sets `LANG=C` and `set -e`, calls `prep-auto-dir`, changes into `build` if an auto-build branch is active, snapshots `configure.sh` to `configure.sh.old` or creates an empty placeholder, runs `prepare-source` or `prepare-source fetch` depending on `.fetch`, diffs the new and old `configure.sh`, and reruns either `./config.status --recheck` or `$srcdir/configure` only when needed. It then runs `./config.status`, `make all`, and `make check` when the first argument is `check`.

## State and Persistence
It modifies build outputs, `configure.sh.old`, generated configure/config files, and build artifacts. It relies on `prep-auto-dir` for persistent build-directory state.

## Dependencies and Integration Points
It integrates with `prep-auto-dir`, `prepare-source`, Autoconf-generated `configure.sh`, `config.status`, and Make. It is also referenced by the release workflow as a build-preparation concept, although `release.py` performs its own release-specific configure sequence.

## Risks
The script assumes `configure.sh` changes are the right trigger for reconfigure, which may miss environment or option changes unless `config.status` handles them. It may overwrite `configure.sh.old`. It exits on first failure but does not clean partial build outputs. Running in the wrong directory without expected scripts will fail.

## Test Signals
Exercise no-change and changed-`configure.sh` cases, `.fetch` and non-`.fetch` paths, auto-build and normal layouts, and `check` argument behavior. Confirm that `config.status --recheck` is invoked only when an existing `config.status` and changed configure are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/smart-make -->
