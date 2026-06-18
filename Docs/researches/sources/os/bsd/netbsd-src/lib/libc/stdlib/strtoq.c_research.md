# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtoq.c

Instantiates the shared `_strtol.h` signed parser for `quad_t`. It binds `_FUNCNAME` to `strtoq`, `__INT` to `quad_t`, and limits to `QUAD_MIN`/`QUAD_MAX`.

The actual base handling, whitespace/sign parsing, end pointer, and overflow behavior are provided by the included template.
