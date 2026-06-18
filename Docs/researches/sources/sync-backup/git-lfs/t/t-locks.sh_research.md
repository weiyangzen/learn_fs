# sources/sync-backup/git-lfs/t/t-locks.sh

## Purpose

Tests listing Git LFS locks from the server and local cache. It covers ref mismatches, single lock listing, `--remote` override behavior, SSH via `git-lfs-authenticate`, pure SSH via `git-lfs-transfer`, JSON output, limits, pagination, and cached `--local` listings including failed duplicate-lock cleanup.

## Important APIs, control flow, and dependencies

The tests create remotes with lockable files, call `git lfs lock`, inspect locks using `git lfs locks --path`, `--json`, `--limit`, and `--local`, configure invalid `remote.pushDefault` and `branch.main.pushRemote`, set SSH transfer modes (`never`, `always`, `negotiate`), remove `origin` to prove local cache use, and unlock cached records.

## State, dependencies, integration points, risks, and test signals

State includes server lock records, local lock cache, branch refs, remote config, SSH config, and command logs. Integration points are locks API pagination, remote selection, SSH protocol negotiation, local lock cache persistence, JSON serialization, and unlock cache cleanup. Risks include using the wrong ref, ignoring `--remote`, missing paginated locks, requiring network for `--local`, or leaving stale cache entries after failed/duplicate lock operations. Signals are line counts, greps for paths/owners/IDs, trace greps for SSH helper selection, nonzero failure checks, and zero local locks after unlock cleanup.
