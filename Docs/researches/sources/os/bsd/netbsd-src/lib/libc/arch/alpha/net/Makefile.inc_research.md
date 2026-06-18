# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/net/Makefile.inc

Alpha net build fragment.

Key behavior:
- Notes that `hton*` and `nto*` functions are provided by `../gen/byte_swap_*.S`.
- Adds lint stub sources `Lint_htonl.c`, `Lint_htons.c`, `Lint_ntohl.c`, and `Lint_ntohs.c` to `LSRCS`, `DPSRCS`, and `CLEANFILES`.
- Does not add runtime sources directly.

Dependencies:
- Generic byte-swap assembly and generated lint stubs.
