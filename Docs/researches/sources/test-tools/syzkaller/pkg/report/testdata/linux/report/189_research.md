<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/189 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/189

## Purpose
This fixture validates lockdep parsing for console virtual terminal reads interacting with pipe splice writes. The expected title is `possible deadlock in vcs_read`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The fixture is static report data for Linux lockdep parser coverage. Important frames include `vcs_read`, `pipe_lock`, `lock_acquire`, `__mutex_lock`, `mutex_lock_nested`, `iter_file_splice_write`, `SyS_splice`, `entry_SYSCALL_64_fastpath`, plus dependency-side frames such as `dput`, `done_path_create`, `handle_create`, `devtmpfsd`, `wait_for_completion`, `devtmpfs_create_node`, `device_add`, `device_create_groups_vargs`, and `device_create`.

## Control Flow
The parser finds a circular locking warning and derives the title from the active `vcs_read` stack. The runtime path is splice-based file movement involving a VCS read path and pipe locking, contrasted against devtmpfs device creation acquiring related locks.

## State And Persistence
The file persists a 168-line lockdep trace. Volatile data includes lock class addresses, task ids, path state, and stack addresses. The fixture does not maintain runtime state; it is a golden parser input.

## Dependencies And Integration Points
It depends on lockdep regexes, splice/VFS stack handling, and the syzkaller test harness that compares parser output to headers. It broadens lockdep coverage beyond networking.

## Risks
The parser could choose the common `pipe_lock` or devtmpfs side instead of `vcs_read`. Lockdep sections with several filesystem stacks make report-boundary handling important.

## Test Signals
Checks should confirm `possible deadlock in vcs_read`, `LOCKDEP`, and report text containing the `vcs_read` to `SyS_splice` stack plus the devtmpfs creation dependency side.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/189 -->
