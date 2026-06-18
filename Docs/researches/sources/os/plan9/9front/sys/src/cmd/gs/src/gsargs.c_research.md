# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.c

Purpose: Command-line argument and `@`-file expansion management.

State management: `arg_init` initializes argv traversal and file-open callback. `arg_push_memory_string` pushes an in-memory source onto the same stack used for `@` files, with a maximum depth. `arg_finit` closes any active files and frees memory-backed strings when ownership was supplied.

Parsing: `arg_next` returns argv entries or parses whitespace-separated arguments from files/memory strings. In `@` files, double quotes protect whitespace; backslash-newline joins lines; comments starting with `#` at beginning of line are skipped. It enforces `arg_str_max`, detects unterminated quotes, and recursively opens `@filename` when expansion is enabled.

Utility: `arg_copy` duplicates an argument into Ghostscript memory.

Dependencies and notes: Error handling reports fatal command-line errors through `*code`, `lprintf`, and `errprintf`.
