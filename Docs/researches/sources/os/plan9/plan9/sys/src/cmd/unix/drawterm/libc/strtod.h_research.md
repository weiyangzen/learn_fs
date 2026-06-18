# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.h

This header declares special floating-point helpers for string-to-double code.

Key contents:
- Declares `__NaN`, `__Inf`, `__isNaN`, and `__isInf`.

Important details:
- The declared return type for `__isNaN`/`__isInf` differs from `nan.h`/`nan64.c`, suggesting an older local header variant.
