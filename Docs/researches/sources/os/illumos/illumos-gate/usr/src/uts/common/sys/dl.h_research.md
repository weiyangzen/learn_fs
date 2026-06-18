# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dl.h

## Scope

Complete file read, 67 lines. This header defines a portable two-word long arithmetic type and related routines.

## Public Surface

It includes `sys/isa_defs.h` and defines `dl_t` as a struct containing high and low words. Field order changes based on `_LONG_LONG_LTOH`.

It declares arithmetic helpers:

- `ladd`, `lsub`, `lmul`, `ldivide`
- `lshiftl`
- `llog10`
- `lexp10`

It also declares constants `lzero`, `lone`, and `lten`.

## Behavior And Integration

This is an ABI/support header for code that uses a software double-length integer representation rather than native `long long`.

## Dependencies And Invariants

Correct binary representation depends on endian/word-order macros. The function implementations are elsewhere.

## Risks

The type is layout-sensitive. Mixing objects compiled with different ISA definitions would break interpretation. It is old-style support code and should not be extended without checking all consumers.
