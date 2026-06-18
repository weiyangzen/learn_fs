# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.h

Read completely: 40 lines.

This header defines `struct c32rtombstate`, currently a one-byte dummy placeholder, with a comment that it must match the maximum conversion state actually used by `wcrtomb_l`.

Important interactions: `c16rtomb.c` and `c8rtomb.c` use this type only for compile-time assertions about how much private state can fit inside `mbstate_t`.

Security/reliability notes: the placeholder makes state sizing dependent on the current `wcrtomb_l` implementation. If `wcrtomb_l` grows private state, this header must be updated.
