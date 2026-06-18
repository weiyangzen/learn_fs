# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/enam.c

This generated-style table maps amd64 opcode enum values to printable instruction names. `anames[]` must remain synchronized with the `enum as` order in `6.out.h`.

The list includes base x86 instructions, pseudo-ops, x87 operations, system instructions, conditional moves, 64-bit amd64 operations, media/SSE operations, 3DNow-like entries, return variants, `SWAPGS`, `MODE`, and `LAST`.

The table is consumed by listing/debug formatting code in the compiler and linker. It underpins `%A` formatting, diagnostic output, debug dumps, and assembly listings.

Filesystem relevance is diagnostic rather than runtime: when building Plan 9 kernel or filesystem code, this table makes compiler/linker output readable and allows instruction-level debugging of generated object streams.
