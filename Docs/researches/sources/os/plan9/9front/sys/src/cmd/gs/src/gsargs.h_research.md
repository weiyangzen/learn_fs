# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.h

Purpose: Data structures and declarations for command-line argument iteration.

Structures: Defines `arg_source` as either a `FILE *` or memory string with optional owning memory. Defines `arg_list` with `expand_ats`, callback data, argv cursor/count, nesting depth, fixed parse buffer, and fixed source stack.

Limits and API: `arg_str_max` is 2048 and `arg_depth_max` is 10. Declares initialization, push, finalization, next-argument, and copy functions, plus a convenience `arg_push_string` macro.

Dependencies and notes: The fixed limits avoid dynamic allocation during parsing except when explicitly copying or pushing owned strings.
