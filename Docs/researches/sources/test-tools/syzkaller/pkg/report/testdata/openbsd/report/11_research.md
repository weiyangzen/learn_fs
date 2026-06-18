# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/11

## Purpose

This OpenBSD fixture expects `witness: thread exiting with locks held`. It tests WITNESS detection for a reaper thread that attempts to exit while holding a sleeplock, with panic text and a compact reaper stack.

## Important APIs, Types, and Functions

Relevant reporter logic covers `TITLE:`, WITNESS warning matching, panic extraction, DDB command transcript parsing, and process-table inclusion. Kernel functions include `witness_thread_exit`, `panic`, `db_enter`, and `reaper`.

## Control Flow

The log first lists a held inode `rrwlock`, then panics with `Thread ... cannot exit while holding sleeplocks`. The trace runs through `witness_thread_exit` into `reaper`, and the later DDB `show panic`/`trace` repeats the same path. The title should come from the WITNESS class of bug rather than the volatile thread pointer in the panic.

## State and Persistence Behavior

Persistent evidence includes held lock class, source path, thread/process identifiers, scheduler flags, registers, process list, and allocator state. Parser state should store the stable title and body range without embedding thread addresses into the title.

## Dependencies and Integration Points

This integrates OpenBSD WITNESS exit checks with normal panic report parsing. It also tests that kernel housekeeping threads such as `reaper` can be valid crashing contexts even when no syzkaller executor appears on the top trace.

## Risks and Edge Cases

Using the panic string verbatim would create address-sensitive titles. The parser must also avoid treating the repeated DDB trace as a second crash and must preserve the original WITNESS preamble, which explains the lock context.

## Test Signals

A passing test returns `witness: thread exiting with locks held`, keeps a non-empty report, and includes `witness_thread_exit` plus `reaper` in the stack evidence.
