# sources/test-tools/ltp/testcases/kernel/fs/ftest/libftest.h

## Purpose

`libftest.h` declares the shared helper API used by the `ftest` filesystem stress tests.

## Important APIs, Types, and Functions

It forward-declares `struct iovec` and declares `ft_dumpiov`, `ft_dumpbits`, `ft_orbits`, `ft_dumpbuf`, and `ft_mkname` under the `__LIBFTEST_H__` include guard.

## Control Flow

There is no executable flow; it exposes helper prototypes to C test files.

## State and Persistence Behavior

No state is owned. Callers provide all buffers, bitmaps, and filename storage.

## Dependencies and Integration Points

Included by `ftest01` through `ftest08` and implemented by `libftest.c`.

## Risks and Edge Cases

The header uses `size_t` in a prototype but does not include `<stddef.h>`; current users include other headers first. `ft_mkname`'s buffer-size contract is documented only by comment in the implementation.

## Test Signals

Compile success across all `ftest` sources confirms the prototypes and include order remain compatible.
