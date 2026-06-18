# sources/test-tools/ltp/testcases/kernel/fs/fsstress/xfscompat.h

## Purpose

`xfscompat.h` provides the small subset of XFS compatibility definitions needed to compile `fsstress` in generic non-XFS mode.

## Important APIs, Types, and Functions

It defines `MAXNAMELEN`, `struct dioattr` with direct-I/O alignment fields `d_miniosz`, `d_maxiosz`, and `d_mem`, plus `MIN` and `MAX` macros.

## Control Flow

There is no runtime flow. The header is included only when `NO_XFS` is defined.

## State and Persistence Behavior

No runtime or persistent state is owned here.

## Dependencies and Integration Points

It substitutes for XFS headers in the default LTP `fsstress` build and is used by direct-I/O helpers in `dread_f` and `dwrite_f`.

## Risks and Edge Cases

The file has no include guard, so direct repeated inclusion could redefine macros or `struct dioattr`. The generic direct-I/O values are derived from `st_blksize` in `fsstress.c`, which may not match every filesystem's true direct-I/O constraints.

## Test Signals

Successful `-DNO_XFS` compilation and successful direct-I/O operation selection without XFS headers are the expected signals.
