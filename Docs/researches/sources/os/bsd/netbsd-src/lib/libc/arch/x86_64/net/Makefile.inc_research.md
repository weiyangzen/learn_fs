# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/net/Makefile.inc

## Summary
x86_64 network byte-order build fragment.

## Key Details
- Adds no object sources locally because byte-swap functions come from `../gen/byte_swap_*.S`.
- Adds lint stubs `Lint_htonl.c`, `Lint_htons.c`, `Lint_ntohl.c`, and `Lint_ntohs.c`.
- Adds these generated lint files to `LSRCS`, `DPSRCS`, and `CLEANFILES`.

## Notes
The fragment exists mostly to keep lint coverage aligned with assembler-provided functions.
