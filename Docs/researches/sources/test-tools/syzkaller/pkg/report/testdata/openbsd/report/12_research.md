# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/12

## Purpose

This OpenBSD fixture expects `witness: userret: returning with the following locks held:`. It captures a WITNESS `userret` panic caused by returning to user space while an inode lock remains held.

## Important APIs, Types, and Functions

Reporter functions under test are WITNESS title extraction, panic matching for `witness_warn`, DDB trace parsing, and metadata preservation. Kernel functions include `witness_warn`, `userret`, `syscall`, and `Xsyscall`; the held lock is an exclusive inode `rrwlock`.

## Control Flow

The kernel reports held locks at user return, then panics through `witness_warn`. The stack shows the panic on the syscall return path rather than the original syscall that acquired the lock. The parser must title the report from the WITNESS `userret` diagnostic, not from the generic `panic: witness_warn`.

## State and Persistence Behavior

The fixture preserves the held inode lock address, source location, process flags, registers, process list, and allocator/pool tables. Parser state should keep the stable WITNESS title and type-neutral report body; address-bearing lock details remain evidence only.

## Dependencies and Integration Points

This integrates WITNESS user-return checks with OpenBSD panic parsing and DDB transcript boundaries. It also validates that a colon-ending title in `TITLE:` is preserved exactly.

## Risks and Edge Cases

The `panic: witness_warn` line is too generic for deduplication and must not override the witness message. The original lock acquisition path may be absent, so the reporter has to accept the WITNESS preamble as primary evidence.

## Test Signals

A passing test returns exactly the expected title including the trailing colon and includes `witness_warn` and `userret` in the parsed report.
