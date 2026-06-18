# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.h

Purpose: Declares command-line argument parsing structures and functions.

Key interfaces: `arg_str_max`, `arg_depth_max`, `arg_source`, `arg_list`, `arg_init`, `arg_push_memory_string`, `arg_push_string`, `arg_finit`, `arg_next`, and `arg_copy`.

Integration: Used by Ghostscript startup code to manage argv plus nested `@` files without dynamic parser state except optional pushed strings.

Risks and notes: Fixed-size `cstr` and source stack define hard limits by design.
