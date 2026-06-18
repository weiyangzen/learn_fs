# sources/sync-backup/git-lfs/t/t-fetch-include.sh

## Purpose

Checks that `git lfs fetch --include` fetches an object when any matching path points at it, even when the same OID is referenced by multiple files in different directories.

## Important APIs, control flow, and dependencies

The setup creates a remote repo, tracks `*.big`, writes identical content under `big/a/a1.big` and `big/b/b1.big`, adds several other `.big` files with a second OID, commits, pushes, and then creates two skip-smudge clones. Each clone pulls Git data without LFS media, runs `git lfs fetch --include=big/a` or `--include=big/b`, and verifies the shared object downloads.

## State, dependencies, integration points, risks, and test signals

State includes server objects for two OIDs, local clones without `.git/lfs/objects` content, and path-filter patterns. Integration points are include filter matching, pointer-to-OID discovery, skip-smudge clone behavior, and duplicate OID handling. Risks include stopping after the first nonmatching path for a duplicated OID or matching only leaf filenames. Signals are push progress for two unique objects, `refute_local_object` before fetch, and `assert_local_object` after each include fetch.
