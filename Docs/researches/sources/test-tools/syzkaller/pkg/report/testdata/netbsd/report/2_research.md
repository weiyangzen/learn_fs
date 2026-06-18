# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/2

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/2` is a NetBSD syzkaller report parser fixture for the expected title `page fault in copystr`. It captures a supervisor-mode page fault while a syz executor reaches `copystr` through NetBSD pathname handling and `mknodat` syscall dispatch. The source was read as a complete 1680-line file: the meaningful parser signal is concentrated in the title/header, trap line, stopped frame, stack trace, register dump, process table, and lockdebug availability line; the remainder is a long NetBSD debugger page listing with repetitive `PAGE FLAG PQ UOBJECT UANON` rows that tests report-boundary handling and noise tolerance.

## Important APIs, Types, and Functions

This file is static testdata consumed by syzkaller's report package, not executable Go or kernel code. Relevant syzkaller APIs and types are the report test harness around `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, parser expectations extracted from `TITLE:`, and the NetBSD reporter implementation that recognizes fatal traps, stopped debugger frames, stack frames, and register dumps. Kernel functions and symbols present in the fixture include `copystr`, `pathbuf_maybe_copyin`, `do_sys_mknodat`, `sys_syscall`, and `syscall`. Important diagnostic tokens include `fatal page fault`, `supervisor mode`, `trap type 6 code 0`, `cr2 0`, `Stopped in pid 603.1`, `syz-executor1586`, `--- syscall (number 0) ---`, and `Sorry, kernel not built with the LOCKDEBUG option.`

## Control Flow

During tests, the harness reads the fixture, consumes the leading `TITLE:` expectation, and feeds the remaining console transcript to the NetBSD reporter. The reporter must detect the first fatal page fault despite duplicated/interleaved console text, identify `copystr` as the crash frame from the stopped instruction and stack trace, and avoid using lower-value frames such as `syscall`. The kernel-side flow represented by the stack is `syscall` -> `sys_syscall` -> `do_sys_mknodat` -> `pathbuf_maybe_copyin` -> `copystr`, where `copystr+0xe` executes `lodsb (%rsi)` with `rsi` equal to zero and `cr2 0`, consistent with a null source pointer fault during string copy.

## State and Persistence Behavior

The fixture persists expected parser state as a text file: a title header plus raw NetBSD debugger output. Runtime test state is transient and includes the detected crash start/end offsets, extracted title, crash type, report byte slice, selected frame, and any corruption/noise classification. No kernel state is mutated when the fixture is used. The transcript itself contains volatile kernel state such as LWP IDs, register values, process names, CPU/LWP scheduling states, and physical page metadata; those values are evidence for parsing but should not become brittle title components.

## Dependencies and Integration Points

The file integrates with syzkaller's `pkg/report` NetBSD reporter and generic report tests under `pkg/report/testdata/netbsd/report`. It exercises parser integration with NetBSD trap grammar, kernel debugger stopped-line parsing, stack frame extraction, process table noise, optional lockdebug output, and report truncation after repeated memory/page dumps. At product level, the same parsing path feeds syzkaller crash deduplication, dashboard grouping, reproducer association, and kernel subsystem triage for NetBSD crashes.

## Risks and Edge Cases

The main risk is overfitting to clean stack traces. This fixture contains duplicated `fatal page fault` text, garbled/interleaved console fragments, two trap lines with different stack pointers, raw register output, a large process table, no LOCKDEBUG build, and thousands of repetitive page rows. A robust parser must still select `page fault in copystr`, not a generic `fatal page fault`, not `pathbuf_maybe_copyin`, and not a repeated address/table token. It must also avoid treating the page metadata tail as a second report or extending the crash title with volatile addresses and PID values.

## Test Signals

A passing test should find a crash in the fixture, return the expected title `page fault in copystr`, preserve a non-empty report body, and keep `ParseFrom` behavior stable around the detected offsets. Strong additional signals are that the parser tolerates interleaved trap text, recognizes the stopped instruction line, chooses the first semantic crashing kernel frame, ignores process-table and page-list noise, and does not require LOCKDEBUG output to be present.
