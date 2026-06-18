# sources/sync-backup/git-lfs/t/t-batch-storage-retries-ratelimit.sh

## Purpose
Tests delayed retry behavior for storage-object HTTP requests, distinct from batch API retries. It covers upload, download, clone-time download, and missing Retry-After header behavior.

## Important APIs, Functions, and Control Flow
The tests use repository names that cause the test server to rate-limit storage endpoints. They commit LFS objects, push or pull/clone under `GIT_TRACE=1`, and count both `tq: retrying object` and `tq: enqueue retry`. Download tests avoid smudge during clone with disabled filters, then run explicit `git lfs pull`.

## State, Persistence, and Dependencies
State includes Git config, local repositories, server object store, object caches, and logs. Dependencies include `setup_remote_repo`, `clone_repo`, `assert_server_object`, `assert_local_object`, and the server's rate-limit fixtures.

## Integration Points, Risks, and Test Signals
Integration is with the transfer queue's storage request retry path. Test signals are retry log counts and successful object assertions. Risks are exact retry-count coupling and shared server state if repository names are reused.
