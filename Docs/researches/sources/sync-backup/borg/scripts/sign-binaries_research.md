# sources/sync-backup/borg/scripts/sign-binaries

## Purpose
This release helper signs every `dist/borg-*` artifact with a detached ASCII-armored GPG signature and then normalizes timestamps in `dist/` to a supplied timestamp. It is intended for Borg release/binary distribution workflows, not runtime execution.

## Important APIs, Types, and Functions
- Positional argument `$1` is required and expected in a `touch -t` compatible format, shown as `201912312359`.
- `$QUBES_GPG_DOMAIN` selects the signing command. When unset, it uses `gpg`; when set, it uses `qubes-gpg-client-wrapper`.
- The `for file in dist/borg-*` loop signs each matching artifact with local user `"Thomas Waldmann"`, writing `$file.asc`.
- `touch -t "$D" dist/*` adjusts timestamps on all files in `dist`.

## Control Flow
The script validates that the timestamp argument is present, selects the GPG wrapper, iterates over distribution artifacts, signs each one, then touches the directory contents after signing. There is no `set -e`, so a failed signature command does not automatically abort later signatures or the timestamp rewrite.

## State and Persistence Behavior
It writes persistent `.asc` signature files next to artifacts in `dist/` and mutates file mtimes for everything matching `dist/*`. It relies on the user's local GPG or Qubes GPG configuration and private key availability. It does not create logs, lock files, or rollback state.

## Dependencies and Integration Points
The script depends on Bash, `gpg` or `qubes-gpg-client-wrapper`, `touch`, the `dist/` directory, and release artifacts named `borg-*`. It integrates with packaging outputs produced by setup/build tooling and complements `scripts/upload-pypi`, which uploads a source distribution.

## Risks and Edge Cases
- Missing `set -euo pipefail` means signing failures can be missed.
- If `dist/borg-*` has no matches, Bash's default unmatched glob behavior leaves the literal string, causing an attempted signature of `dist/borg-*`.
- The signing identity is hard-coded; release maintainers using different keys must edit the script or configure GPG accordingly.
- `touch -t "$D" dist/*` mutates all files under `dist`, including signatures and unrelated files.

## Test Signals
Test with a temporary `dist/` containing sample files and a fake `gpg` on `PATH` to assert arguments and `.asc` outputs. Check that a missing timestamp exits nonzero, that `QUBES_GPG_DOMAIN` switches the command, and that invalid timestamps cause an observable failure. Release validation should verify signatures with `gpg --verify`.
