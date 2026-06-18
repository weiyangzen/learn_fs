# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdalign.h

## Role

Implements ISO C11 `<stdalign.h>` support for illumos system headers.

## Key Contents

For C, maps `alignas` to `_Alignas` and `alignof` to `_Alignof`. For C++, it avoids redefining keywords but still defines `__alignas_is_defined` and `__alignof_is_defined`.

## Design Notes

The header intentionally does not add compiler feature guards beyond C++ handling. It assumes C11 or newer use and lets missing compiler support surface as a compiler error.
