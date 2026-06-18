# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.c

Purpose: Implements Ghostscript command-line argument list parsing with nested `@` file expansion.

Key interfaces: `arg_init`, `arg_push_memory_string`, `arg_finit`, `arg_next`, and `arg_copy`.

Control flow: initialization points at `argv[1]` and enables `@` expansion. Sources can be argv, files, or pushed memory strings. `arg_next` reads tokens, skips whitespace, supports comments beginning with `#` at line start in `@` files, supports quote-protected whitespace in `@` files, treats backslash-newline as continuation, expands leading `@` by opening another file, and enforces max argument length/depth. Cleanup closes open files and frees owned memory strings.

Dependencies: Uses Ghostscript memory allocation, error constants, stdio, ctype, and caller-supplied `arg_fopen`.

Risks and notes: Arguments longer than 2048 bytes or nesting deeper than 10 levels are fatal. Quoting is only honored for file-backed sources, not raw argv.
