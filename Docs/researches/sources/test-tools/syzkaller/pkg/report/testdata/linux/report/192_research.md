<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/192 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/192

## Purpose
This fixture verifies a longer perf lockdep report where the expected title is `possible deadlock in perf_event_init_task`, type `LOCKDEP`. It covers fork/task initialization interactions with perf trace initialization and splice/read paths.

## Important APIs, Types, And Functions
The static fixture exercises lockdep parsing across 312 lines. Important frames include `perf_trace_init`, `perf_event_init_task`, `perf_event_ctx_lock_nested`, `perf_read`, `do_iter_read`, `vfs_readv`, `default_file_splice_read`, `do_splice_to`, `SyS_splice`, `do_fast_syscall_32`, `entry_SYSENTER_compat`, `pipe_lock`, `iter_file_splice_write`, `fs_reclaim_acquire`, and `kmem_cache_alloc`.

## Control Flow
The Linux reporter parses the warning and dependency graph, then selects `perf_event_init_task` as the meaningful owner rather than the first visible frame `perf_trace_init`. The runtime evidence crosses compat syscalls, readv/splice handling, perf read locking, and task initialization.

## State And Persistence
The file persists the expected title and type plus a long lockdep report. Volatile state includes lock names with class ids, allocation contexts, task ids, and syscall ABI details. The fixture itself is immutable test input.

## Dependencies And Integration Points
It integrates with lockdep parsing, compat syscall frame normalization, perf event title heuristics, and report-boundary logic for long dependency reports.

## Risks
Because `perf_trace_init` appears above `perf_event_init_task`, simple first-frame selection would produce the wrong title. Long reports also risk losing dependency context or selecting `fs_reclaim_acquire` from a nested section.

## Test Signals
Assert exact title `possible deadlock in perf_event_init_task` and `LOCKDEP`. The report should retain the perf initialization frames and the splice/read path that exposes the lock cycle.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/192 -->
