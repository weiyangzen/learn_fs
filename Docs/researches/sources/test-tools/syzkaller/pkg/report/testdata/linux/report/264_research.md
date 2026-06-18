<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/264 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/264

## Purpose
This fixture tests soft-lockup parsing for directory removal. The expected title is `BUG: soft lockup in sys_rmdir`, alternates for `__x64_sys_rmdir` and generic stall spellings, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
Headers include `TITLE`, multiple `ALT` entries, `TYPE`, and `PANICKED`. Parser paths include watchdog soft-lockup matching, syscall-name normalization, alternate title generation, and panic detection. Important symbols include `d_walk`, `shrink_dcache_parent`, `vfs_rmdir`, `do_rmdir`, `__x64_sys_rmdir`, `select_collect`, `dump_stack`, `panic`, `watchdog_timer_fn.cold.5`, and hrtimer/APIC frames.

## Control Flow
The reporter reads a `watchdog: BUG: soft lockup` report, task register dump, call trace through the rmdir path, a second CPU stack, and a final softlockup panic. It must normalize the syscall-facing title to `sys_rmdir` while retaining alternates for the concrete `__x64_sys_rmdir` frame.

## State and Persistence Behavior
The file persists a 110-line soft-lockup log and expected hang metadata. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux soft-lockup patterns, syscall alias normalization, panic recognition, and alternate-title sorting in the test harness.

## Risks and Edge Cases
Multiple CPUs and the later panic stack can displace the original stalled task. The syscall alias logic must stay stable across old `sys_*` and newer `__x64_sys_*` names.

## Test Signals
Expected output includes title `BUG: soft lockup in sys_rmdir`, all listed alternates, type `HANG`, and panic flag true.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/264 -->
