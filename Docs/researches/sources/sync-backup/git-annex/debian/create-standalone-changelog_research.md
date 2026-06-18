<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/debian/create-standalone-changelog -->
# sources/sync-backup/git-annex/debian/create-standalone-changelog

Purpose: Debian helper script for generating a NeuroDebian changelog entry for a standalone git-annex package snapshot.

Important operations: runs with `set -eu`, sets `umask 022`, derives `ANNEX_VERSION` from `git describe HEAD`, transforms it into `ANNEX_NDVERSION` by replacing the first dash with `+git` and appending `-1~ndall+1`, then invokes `dch` with forced version/distribution flags and message `Backported fresh snapshot`.

Control flow and state: the script must run inside the git-annex repository so `git describe HEAD` has meaningful tag context. It mutates Debian changelog state through `dch`; no other files are directly written by the script.

Dependencies and integration points: depends on Git, Debian `devscripts`/`dch`, a usable `debian/changelog`, and NeuroDebian package versioning expectations.

Risks: unquoted variable expansions in the `sed` pipeline and `dch` call are acceptable for typical Git describe values but not robust for pathological tag strings. `--force-bad-version` and `--force-distribution` bypass safeguards, so caller discipline matters.

Test signals: run in a throwaway checkout with known tag layouts, inspect the resulting changelog version sort order, and verify failure when outside a Git repository.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/debian/create-standalone-changelog -->
