# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/5

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/5` is a NetBSD syzkaller report parser fixture for the expected title `lock error in do_sys_accept`. It captures a LOCKDEBUG panic caused by a mutex ownership assertion failure while handling `paccept`/`accept` syscall logic. The source was read as a complete 18-line file.

## Important APIs, Types, and Functions

The file is static report testdata rather than executable code. Relevant syzkaller APIs are the report test harness, `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, `TITLE:` expectation parsing, and NetBSD panic/traceback title extraction. Kernel functions and diagnostics in the transcript include `panic: lock error`, `Mutex: mutex_vector_exit,761`, assertion `MUTEX_OWNER(mtx->mtx_owner) == curthread`, `vpanic`, `snprintf`, `lockdebug_abort`, `mutex_vector_exit`, `do_sys_accept`, `sys_paccept`, `sys___syscall`, and `syscall`. The syscall marker is `--- syscall (number 198) ---`.

## Control Flow

The test harness reads the expected title and feeds the panic transcript to the NetBSD reporter. The parser must identify the lock-error panic, walk the traceback, and choose `do_sys_accept` as the semantic crashing frame rather than generic panic helpers or lockdebug internals. The represented kernel flow is syscall entry -> `sys___syscall` -> `sys_paccept` -> `do_sys_accept` -> `mutex_vector_exit`; the lockdebug subsystem detects that the current LWP does not own the mutex being released and triggers `lockdebug_abort`/`vpanic`.

## State and Persistence Behavior

The fixture persists the expected parser title plus a concise panic and reboot transcript. Runtime parser state is transient: detected panic offset, traceback frame list, selected title frame, report bytes, and end offset near dump/reboot lines. Kernel state in the log includes a mutex address, CPU number, LWP pointer, dump device, and reboot action; those values are volatile and should remain body evidence, not title components. No external state is changed by running the parser test.

## Dependencies and Integration Points

This fixture integrates with NetBSD panic parsing, LOCKDEBUG assertion recognition, traceback frame filtering, syscall wrapper handling, and panic dump/reboot boundary detection. It protects the path that syzkaller uses to group NetBSD locking bugs by the kernel subsystem frame (`do_sys_accept`) instead of by shared helpers such as `vpanic`, `lockdebug_abort`, or `mutex_vector_exit`. Downstream, this improves deduplication and triage for socket accept path locking regressions.

## Risks and Edge Cases

The title extractor must filter generic frames carefully. Selecting `mutex_vector_exit` would identify the failed primitive but lose the owning subsystem, while selecting `vpanic` or `lockdebug_abort` would collapse unrelated lock bugs together. The parser also needs to tolerate compact logs with no register dump or process table, retain the panic line as report evidence, and stop cleanly around `dumping ... not possible` and `rebooting...`.

## Test Signals

A passing test detects the panic and returns exactly `lock error in do_sys_accept` with a non-empty report. Strong signals include recognizing `panic: lock error` as the crash start, selecting the first meaningful non-helper traceback frame, preserving syscall context in the report body, and keeping dump/reboot lines inside or at the boundary of the parsed report without creating extra crashes.
