# File Research: sources/os/bsd/freebsd-src/sys/sys/rangelock.h

Read completely: 105 lines.

## Purpose
Defines range-lock state and kernel APIs for read/write locking byte ranges with overlap-aware compatibility.

## Main Elements
- Defines read/write lock type bits and type mask.
- Defines `struct rangelock` with packed head, sleeper state, and reserved fields intended for embedding consumers.
- Documents compatibility: non-overlapping ranges can coexist; overlapping readers can coexist; overlapping writers conflict.
- Declares initialization, destruction, unlock, blocking and try read/write lock operations, recursion allowance, and invariant cookie assertions.
- Defines assertion flags for locked/read-locked/write-locked cookies.

## Dependencies And Integration
Used by kernel consumers needing byte-range exclusion, notably vnode/file-style range coordination. Depends on VM offset types and invariant support.

## Risk Notes
The returned cookie represents lock ownership and must be released exactly once. Embedded reserved fields are intentionally available to consumers, so structure layout is part of an internal KPI.
