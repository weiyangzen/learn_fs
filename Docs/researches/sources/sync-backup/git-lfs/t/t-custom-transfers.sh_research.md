# sources/sync-backup/git-lfs/t/t-custom-transfers.sh

## Purpose

Tests Git LFS custom transfer adapters and standalone transfer-agent selection across HTTP, local file, and pure SSH remotes. It verifies failure for an invalid custom adapter path, successful upload/download through configured test adapters, URL-specific standalone agent lookup, and safeguards around internal standard adapters such as `basic`, `ssh`, and `lfs-standalone-file`.

## Important APIs, control flow, and dependencies

The script uses `begin_test`/`end_test`, `setup_remote_repo`, `clone_repo`, `clone_repo_url`, `setup_pure_ssh`, `git config lfs.customtransfer.*`, `lfs.standalonetransferagent`, `remote.origin.lfsurl`, `git lfs track`, `lfstest-testutils addcommits`, `git push`, `git lfs fetch --all`, `git lfs pull`, `git lfs fsck`, and object assertion helpers. Control flow is a set of isolated repos: configure transfer settings, generate LFS-tracked `.dat`/`.bin` data, push, clear `.git/lfs/objects`, fetch or pull, then grep trace output and verify object storage.

## State, dependencies, integration points, risks, and test signals

Persistent state includes local `.git/lfs/objects`, remote/server object stores, `TEST_STANDALONE_BACKUP_PATH`, and per-repo Git config. Integration points are the LFS transfer queue, batch API transfer negotiation, standalone adapter process protocol, file URL adapter, URL config matching, lock verification bypass for standalone transfers, and SSH transfer support. Risks include silently falling back from a broken adapter, accepting the file adapter for HTTP remotes, standard/custom adapter name conflicts, quoting bugs in adapter args, and duplicate transfers under concurrency. Signals are transfer trace lines, expected nonzero push/pull failures, `Uploading LFS objects: 100%`, object counts, local/remote object assertions, and warning/error grep checks.
