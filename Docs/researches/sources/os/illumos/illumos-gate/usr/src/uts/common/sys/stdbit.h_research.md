# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbit.h

## Role

Implements C23 `<stdbit.h>` functionality for illumos, with usable non-generic functions across C versions and type-generic macros when C11 `_Generic` is available.

## Key Contents

Defines `__STDC_VERSION_STDBIT_H__`, endian constants, native endian selection, and `size_t` if needed. Declares extern functions for leading/trailing zeros and ones, first leading/trailing zero/one, zero/one counts, single-bit test, bit width, bit floor, and bit ceiling for unsigned char, unsigned short, unsigned int, unsigned long, and conditionally unsigned long long.

## Generic Macros

When `_STDC_C11` is defined, maps generic `stdc_*` macros by `sizeof(val)` to 1-, 2-, 4-, or 8-byte implementations using `_Generic` on a fixed-length array pointer expression.

## Design Notes

The implementation deliberately uses extern functions provided by libc and the kernel rather than relying on compiler builtins or inline expansion, avoiding runtime support mismatches.
