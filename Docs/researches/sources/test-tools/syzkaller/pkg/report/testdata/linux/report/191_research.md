<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/191 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/191

## Purpose
This fixture validates lockdep extraction for perf event context locking during splice activity. Expected title is `possible deadlock in perf_event_ctx_lock_nested`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The report-test file uses `TITLE` and `TYPE` headers with a 248-line lockdep trace. Important frames include `perf_event_ctx_lock_nested`, `pipe_lock`, `lock_acquire`, `__mutex_lock`, `mutex_lock_nested`, `iter_file_splice_write`, `SyS_splice`, `try_to_wake_up`, `default_wake_function`, `__wake_up_common`, `complete`, `wait_for_completion`, `devtmpfs_create_node`, `device_add`, `device_create_groups_vargs`, and `device_create`.

## Control Flow
The parser detects the circular locking dependency and must choose the perf context lock helper as the title. The runtime flow shows splice/pipe locking interacting with wakeups and device creation, with perf event context locking participating in the cycle.

## State And Persistence
Persistent state is the lockdep log and expected metadata. Lock graph entries, pointer values, task names, and CPU ids are volatile. There is no code path in this repository besides the parser test harness consuming the data.

## Dependencies And Integration Points
It depends on Linux lockdep report parsing and perf stack naming. It integrates through syzkaller's report fixtures and helps ensure perf lock helpers are retained as meaningful titles rather than filtered as generic lock internals.

## Risks
The parser may over-filter `perf_event_ctx_lock_nested` as a helper and choose `pipe_lock` or splice instead. Long lockdep reports also risk truncation that can change the selected frame.

## Test Signals
Stable checks are title `possible deadlock in perf_event_ctx_lock_nested`, type `LOCKDEP`, and preservation of perf, pipe, splice, and wakeup/device dependency stacks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/191 -->
