# sources/test-tools/ltp/testcases/kernel/fs/ftest/libftest.c

## Purpose

`libftest.c` provides shared diagnostic and naming helpers for the `ftest` legacy filesystem tests.

## Important APIs, Types, and Functions

Exported functions are `ft_dumpiov`, `ft_dumpbits`, `ft_orbits`, `ft_dumpbuf`, and `ft_mkname`. They format iovec/buffer/bitmap diagnostics through `tst_resm`, OR bitmap arrays, and generate deterministic two-letter child/iteration names.

## Control Flow

The dump functions compress runs of repeated bytes and stop after enough segments to avoid huge output. `ft_orbits` loops over `size` bytes and ORs `bits` into `hold`. `ft_mkname` uses `me % 26` and `idx % 26` to create names under an optional directory.

## State and Persistence Behavior

The library owns no persistent state. It writes only test log output and caller-provided buffers.

## Dependencies and Integration Points

It depends on `test.h`, `<sys/uio.h>`, integer formatting headers, and `libftest.h`. All `ftestNN` binaries link it via the local Makefile.

## Risks and Edge Cases

`ft_mkname` can collide after 26 children or 26 indices and assumes the destination buffer is `PATH_MAX`-sized. `ft_dumpbits` uses pointer arithmetic on `void *`, a GNU extension. Diagnostic helpers are not thread-safe but are used in forked children.

## Test Signals

Useful signal is improved failure output: compact iovec, buffer, and bitmap dumps that explain where sparse-file expectations diverged.
