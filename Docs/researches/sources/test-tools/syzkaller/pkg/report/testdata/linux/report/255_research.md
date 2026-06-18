<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/255 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/255

## Purpose
This is another hung-task console-device fixture, from a different 4.4 kernel log. It should parse to `INFO: task hung in console_device`, alternate `hang in console_device`, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The file uses standard report headers and a raw hung-task log. Parser paths include task-hang oops matching, blocked-task stack extraction, title normalization, and panic detection. Representative symbols include `schedule`, `schedule_timeout`, `__down`, `down`, `console_lock`, `console_device`, `tty_open`, `chrdev_open`, `do_dentry_open`, `path_openat`, `do_sys_open`, `SyS_open`, and `watchdog`.

## Control Flow
The Linux reporter starts at the `INFO: task init:1 blocked for more than 120 seconds` section, extracts the blocked stack through `console_lock` and `console_device`, then observes NMI backtraces and the `Kernel panic - not syncing: hung_task: blocked tasks` line. The chosen title must remain tied to the blocked task, not the watchdog/panic section.

## State and Persistence Behavior
The fixture stores expected metadata and a 168-line raw log. No mutable state or persistence beyond checked-in test data exists.

## Dependencies and Integration Points
It depends on hung-task parser rules, function skip lists, panic recognition, and generic `ParseTest` comparison.

## Risks and Edge Cases
Because it is similar to report 254 but not identical, it guards against overfitting to one kernel's symbol offsets and against selecting NMI backtrace frames.

## Test Signals
The expected parse is the same HANG title/alt/panic tuple centered on `console_device`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/255 -->
