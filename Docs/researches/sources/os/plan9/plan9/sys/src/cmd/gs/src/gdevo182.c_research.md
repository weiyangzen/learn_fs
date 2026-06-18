# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevo182.c

Okidata Microline 182 dot-matrix printer driver.

- Defines `oki182`, a 1-bit printer device defaulting to 8x11 inches at 72 dpi.
- Supports 72x72 and 144x144 modes, with comments describing required printer DIP switch setup and 8-bit graphics mode assumptions.
- `oki_transpose` converts 7 scan lines into vertical 7-bit column bytes with the high bit set to avoid command-byte confusion.
- `oki_compress` trims trailing blank graphics bytes and converts long leading blank runs into spaces; high-resolution mode doubles columns per space.
- `oki_print_page` initializes printer mode, skips blank rows using fine line feed commands, gathers 7 or 14 scan lines, transposes them, compresses output, and emits printer command/data sequences.
- High-resolution mode splits even/odd scan lines into two graphics passes with a one-bit line feed between them.
- Always emits a form feed and flushes before freeing buffers.
- Risk notes: printer command protocol is tightly coupled to hardware behavior; write calls mostly ignore short-write/error status.
