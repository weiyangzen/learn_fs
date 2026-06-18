# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/6

## Purpose

This 1242-line fixture is a NetBSD syzkaller report parser test for the expected title `ASan: Unauthorized Access in sys__lwp_getname`. It captures a KASAN/ASan panic from a read during `kasan_copyoutstr` while servicing syscall 198, with enough debugger, process, lock, malloc, pool, and reboot context to exercise long-report capture and title normalization.

## Important APIs, Types, and Functions

The file is static testdata, so the important APIs are syzkaller reporter behaviors: metadata parsing from `TITLE:`, crash detection from `panic: ASan: Unauthorized Access`, extraction through `Reporter.Parse`, frame filtering, and report-end detection. Kernel evidence includes `vpanic`, `snprintf`, `kasan_report`, `kasan_copyoutstr`, `sys__lwp_getname`, `sys___syscall`, `syscall`, `breakpoint`, `db_panic`, and the syscall marker `--- syscall (number 198) ---`.

## Control Flow

The represented kernel flow is syscall entry through `sys___syscall` into `sys__lwp_getname`, followed by `kasan_copyoutstr` checking a user copyout string and reporting an unauthorized read. The panic enters DDB, emits a second symbolic traceback, register state, LWP/process tables, locks, allocator summaries, and dump/reboot lines. The parser must choose the actionable syscall frame, not helper frames such as `vpanic`, `snprintf`, `kasan_report`, or `kasan_copyoutstr`.

## State and Persistence Behavior

The fixture persists volatile runtime addresses, CPU/LWP identifiers, multiple `syz-executor` processes, held locks, pool statistics, and dump metadata. Parser state should remain transient: crash start offset, selected title, body bytes, and end offset. None of the allocator counts, addresses, timestamps, or process IDs should be used as stable title material.

## Dependencies and Integration Points

This case integrates NetBSD panic matching, sanitizer report normalization, DDB transcript handling, traceback frame selection, and long-report boundary handling. It also exercises the path where the initial timestamped kernel log and the later DDB traceback both describe the same crash.

## Risks and Edge Cases

The title must normalize `Unauthorized Access In ...` to the expected `ASan: Unauthorized Access in sys__lwp_getname` while preserving the crash body. A naive frame picker could group under KASAN helpers, and a naive end detector could truncate before lock/pool context or accidentally treat later debugger output as a second crash. Syslog-like timestamps and repeated stack frames must not destabilize deduplication.

## Test Signals

A passing test returns exactly the expected title, produces a non-empty report containing the ASan panic and `sys__lwp_getname` frame, and keeps the complete DDB evidence as one crash report. The strongest signal is correct selection of `sys__lwp_getname` as the first meaningful non-sanitizer kernel frame.
