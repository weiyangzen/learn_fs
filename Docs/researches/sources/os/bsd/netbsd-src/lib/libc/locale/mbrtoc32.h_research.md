# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.h

Read completely: 40 lines.

This header defines `struct mbrtoc32state`, currently a one-byte dummy placeholder, with a note that it must match the maximum state actually used by `mbrtowc_l`.

Important interactions: `mbrtoc16.c` and `mbrtoc8.c` use it for compile-time `mbstate_t` layout assertions.

Security/reliability notes: if `mbrtowc_l` starts using more private state, this placeholder must be updated or the assertions may become misleading.
