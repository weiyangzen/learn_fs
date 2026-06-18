# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zgeneric.c

## Purpose
Implements generic PostScript operators shared by arrays, strings, dictionaries, packed arrays, and byte structures: `copy`, `get`, `put`, `length`, intervals, and `forall`.

## Key Functions
- `zcopy()`, `zcopy_integer()`, and `zcopy_interval()` implement stack, array, string, and dictionary copy dispatch.
- `zlength()`, `zget()`, and `zput()` implement common composite object access.
- `zforceput()` bypasses normal access checks for selected internal use.
- `zgetinterval()` and `zputinterval()` handle subsequence extraction and replacement.
- `zforall()` schedules iteration continuations for arrays, dictionaries, strings, and packed arrays.
- `copy_interval()` performs the shared array/string/packed-array copy logic.

## Important Behavior
- Stack copy has a fast contiguous-stack path and a general multi-block path.
- Dictionary `put` honors superexec bypass and otherwise enforces write permissions.
- Packed arrays are read-only for mutation.
- `forall` uses the execution stack to preserve iteration state and call user procedures.
- Array copies use old-generation-aware ref assignment; strings use `memmove` for aliasing.

## Research Notes
Core interpreter object plumbing; heavily tied to VM, stacks, packed arrays, and dictionary internals.
