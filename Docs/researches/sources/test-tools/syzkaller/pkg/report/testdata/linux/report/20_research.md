<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/20 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/20

## Purpose
This compact fixture tests corrupted NULL pointer dereference parsing. It expects title `BUG: unable to handle kernel NULL pointer dereference in corrupted`, alt `bad-access in corrupted`, type `NULL-POINTER-DEREFERENCE`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The file contains metadata plus an eight-line log with `BUG: unable to handle kernel NULL pointer dereference at 000000000000058c` and an `__lock_acquire` frame. Parser behavior under test includes NULL dereference recognition, corrupted-title selection, and not overfitting to a lone lockdep frame.

## Control Flow
The reporter sees the page fault/null-deref signature but lacks a reliable non-corrupted stack. It should therefore produce the corrupted title and bad-access alternate rather than `__lock_acquire`.

## State And Persistence
The persistent state is the expected metadata and a short crash line. The fault address is dynamic except for the null-range signal. No mutable state exists.

## Dependencies And Integration Points
It depends on Linux page-fault and null-deref matchers, corrupted-report heuristics, and crash type mapping to `NULL-POINTER-DEREFERENCE`.

## Risks
The parser could emit `BUG: unable to handle kernel NULL pointer dereference in __lock_acquire` or a generic bad-access title. Very short input also tests behavior with incomplete reports.

## Test Signals
Exact title, alt, type, and `CORRUPTED: Y` should remain stable. The fixture should not produce a lockdep title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/20 -->
