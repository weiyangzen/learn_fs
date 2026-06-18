# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/log.h

Header for `slaacd` logging.

Contents:
- Declares logging, verbosity, and fatal APIs with printf-format attributes.
- Includes `stdarg.h` and `stdlib.h`.
- Under `SMALL`, compiles logging calls to no-ops and maps fatal exits to `exit(1)`.

Role:
- Allows the same source tree to build full daemon/control variants and reduced `SMALL` variants.
- Provides compile-time format checking for normal builds.
