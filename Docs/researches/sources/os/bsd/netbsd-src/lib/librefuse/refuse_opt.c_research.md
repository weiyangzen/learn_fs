# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_opt.c

This file implements FUSE option parsing and argument-vector manipulation. It supports deep-copying and freeing `struct fuse_args`, appending and inserting args, composing comma-separated `-o` option strings with optional escaping, matching templates with `=` or space separators, and parsing all argv entries into a filtered output vector.

The parser treats program name as kept, handles `--`, `-ofoo` and `-o foo`, parses comma-separated option lists with backslash escaping, supports templates like `foo=%s` and `-x %d`, writes parsed values into offsets, and calls optional processors for keep/discard/error decisions.

Risks: `%s` values are heap-allocated into caller-provided fields without freeing prior contents, nonliteral `sscanf` formats are used by design, and ownership swaps between input and output `fuse_args` must be handled exactly to avoid leaks or double frees.
