# sources/sync-backup/git-lfs/t/t-batch-retries-ratelimit.sh

## Purpose
Tests retry behavior when the batch API itself returns rate-limit responses. It covers upload, multi-object upload, clone/download, multi-object clone/download, and missing Retry-After header behavior.

## Important APIs, Functions, and Control Flow
Each test creates LFS-tracked files, pushes or clones under `GIT_TRACE=1`, and counts `tq: enqueue retry` log entries. Download tests use `set_server_rate_limit "batch"` to avoid rate limiting the initial push and then force rate limiting on the clone. Missing-header upload expects more than one retry and specific retry ordinals.

## State, Persistence, and Dependencies
The tests mutate remote server rate-limit state, local repositories, LFS objects, and trace logs. They depend on `setup_remote_repo`, `clone_repo`, `set_server_rate_limit`, `assert_server_object`, and `assert_local_object`.

## Integration Points, Risks, and Test Signals
Integration is with transfer queue retry scheduling for batch metadata requests. Signals include retry count, retry ordinal messages, successful server/local object assertions, and zero command failures. Risks are timing and delay behavior in rate-limit tests, plus brittle dependence on trace message wording.
