# sources/storage-engines/wiredtiger/test/format/format_disagg.c

## Purpose
`format_disagg.c` manages disaggregated-storage test orchestration, including multi-node leader/follower setup, output redirection, interprocess synchronization, optional hash validation, role switching, and teardown.

## Important APIs, Types, And Functions
Key functions are `disagg_setup_multi_node`, `disagg_teardown_multi_node`, `disagg_sync_multi_node`, `disagg_is_multi_node`, `disagg_is_mode_switch`, and `disagg_switch_roles`. Static helpers include `disagg_redirect_output` and `disagg_multi_sync_point`. It uses `fork`, `socketpair`, `mmap`, `munmap`, `freopen`, `dup2`, `wts_reopen`, `follower_read_latest_checkpoint`, `timestamp_sync_threads_commit_ts`, and `wts_verify_mirrors`.

## Control Flow
Setup checks whether multi-node disaggregation is enabled, creates leader/follower home directories when not reopening, initializes shared page-log home and shared hash memory, creates a socket pair, and forks. The child becomes follower, rewrites config to follower mode, changes home, redirects output, and keeps one socket end. The parent becomes leader, redirects output, and tracks the child PID. Synchronization writes and reads one byte on the socket. Validation computes per-node database hashes, synchronizes, optionally preserves mismatch state, synchronizes again, then asserts equality. Role switching toggles `g.disagg_leader`; stepping down reopens as follower and picks up a checkpoint, while stepping up reconfigures to leader, advances timestamps, checkpoints, and verifies mirrors.

## State And Persistence Behavior
The file persists node logs as `leader.out` and `follower.out`, creates `follower/` under the run home, shares `DISAGG_MULTI_DB_HASH` through anonymous shared memory, and mutates global role/page-log/sync fields. Role switch and sync operations persist WiredTiger checkpoints and disaggregated metadata through reconfiguration and checkpoints.

## Dependencies And Integration Points
It depends on config normalization for `disagg.page_log`, `disagg.multi`, `disagg.mode`, `disagg.multi_validation`, and `disagg.preserve`; on `checksum_database`; on follower checkpoint pickup; on timestamp and verification subsystems; and on POSIX process/socket APIs.

## Risks And Test Signals
Risks include forked process divergence, socket deadlocks, shared-memory cleanup leaks, follower timeout during teardown, role-switch checkpoint gaps, and hash mismatches. Signals include leader/follower logs, synchronization track messages, preserved disagg state on mismatch, child process timeout, and mirror/hash assertions.
