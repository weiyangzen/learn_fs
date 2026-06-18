# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.h

Declares timeval helper functions and portability macros.

Definitions:
- Includes `<sys/time.h>`.
- Defines `timeval_isset(tv)` if absent.
- Defines `timeval_clear(tv)` if absent.

Public API:
- `timeval_subtract`.
- `timeval_add`.
- `timeval_divide`.
- `timeval_smaller`.

Usage note:
- No include guard is present in this header, but contents are simple declarations/macros.
