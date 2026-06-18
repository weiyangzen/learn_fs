# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbool.h

## Role

Implements ISO C99 `<stdbool.h>` compatibility.

## Key Contents

Includes feature-test definitions and, outside C++, defines `bool` as `_Bool`, `true` as `1`, `false` as `0`, and `__bool_true_false_are_defined` when C99 features or compatible compiler support are available.

## Design Notes

The header notes that undefining/redefining `bool`, `true`, and `false` is obsolescent but preserved for standards compatibility.
