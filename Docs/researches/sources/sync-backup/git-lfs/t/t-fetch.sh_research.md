# sources/sync-backup/git-lfs/t/t-fetch.sh

## Purpose

Comprehensive integration coverage for `git lfs fetch`: normal fetch, dry-run, JSON output, refetch of corrupt objects, shared repositories, remote/branch/commit arguments, stdin refs, include/exclude filters, missing objects, SSL key errors, `--all`, bare repos, no-origin default remote selection, prune, raw remote URLs, invalid inputs, and permission failures.

## Important APIs, control flow, and dependencies

The setup creates a remote with `a.dat` on `main`, `b.dat` on `newbranch`, an empty `.dat`, a clone, and a shared clone. Tests repeatedly clear `.git/lfs/objects`, run `git lfs fetch` variants, compare JSON against expected transfer action payloads, corrupt objects, delete server objects, generate a multi-branch/tag `fetch-all` fixture with `lfstest-testutils addcommits`, create a bare clone, and exercise `--stdin`.

## State, dependencies, integration points, risks, and test signals

State includes local object cache, remote object store, shared Git object database, refs/tags/branches, bare-repo LFS storage, path filters, corrupt object files, and filesystem permissions. Integration points are batch API action rendering, JSON serialization, object integrity checking, ref walking, raw URL endpoint creation, prune logic, SSL credential loading, and default remote selection. Risks include dry-run writing objects, refetch deduplicating incorrectly, `--all` missing tag-only or remote-only refs, pruning needed objects, failing in shared repos, or poor error handling for invalid remotes/refs and unwritable storage. Signals include exact push/fetch progress greps, JSON diffs, fsck OK output, object presence matrices, nonzero status for missing objects, and permission/error message greps.
