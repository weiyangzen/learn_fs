<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/254 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/254

## Purpose
This fixture verifies hung-task parsing for console device opens. The expected title is `INFO: task hung in console_device`, alternate `hang in console_device`, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, `TYPE`, and `PANICKED`. Parser functions under test include hung-task detection, stack extraction, alternate hang-title generation, and panic detection. Important symbols include `schedule`, `schedule_timeout`, `__down`, `down`, `console_lock`, `console_device`, `tty_open`, `chrdev_open`, `do_dentry_open`, `path_openat`, `SyS_open`, `watchdog`, and `panic`.

## Control Flow
The reporter sees an `INFO: task init... blocked for more than 120 seconds` section, repeated blocked `init` task stacks, NMI backtraces, and a final hung-task panic. It must choose the blocked task's meaningful wait site `console_device`, not the later NMI or khungtaskd panic stack.

## State and Persistence Behavior
The fixture persists a large multi-task console log. No runtime state is owned; expected state is the HANG classification, alt title, and panic flag.

## Dependencies and Integration Points
It depends on Linux hung-task regexes, stack collapsing for repeated tasks, panic-line detection, and skip lists for scheduler/wait helpers.

## Risks and Edge Cases
Multiple call traces and NMI backtraces can lure the parser to `io_serial_in`, `watchdog`, or `panic`. The repeated `<Same stack>` style also tests report boundary robustness.

## Test Signals
Stable output is title `INFO: task hung in console_device`, type `HANG`, alt `hang in console_device`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/254 -->
