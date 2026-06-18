# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/64

## Purpose
This minimal fixture covers a corrupted lockdep/spinlock lockup report.

## Important APIs, types, and functions
The raw signal is `BUG: spinlock lockup suspected on CPU#2, syz-executor/12636`. Expected metadata sets `TYPE: LOCKDEP` and `CORRUPTED: Y`.

## Control flow
There is not enough stack information to name a reliable lock holder or caller, so the title is intentionally `in corrupted`.

## State and persistence behavior
The persisted state is the corrupted lockdep classification. The fixture has no mutable behavior.

## Dependencies and integration points
It verifies syzkaller's lockdep recognizer for incomplete spinlock lockup reports.

## Risks and test signals
The parser must not infer a missing frame. Passing behavior preserves `BUG: spinlock lockup suspected in corrupted`.
