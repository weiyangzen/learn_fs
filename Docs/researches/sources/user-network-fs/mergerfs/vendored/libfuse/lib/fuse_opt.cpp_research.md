# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_opt.cpp

## Purpose
`fuse_opt.cpp` implements libfuse-style command-line and `-o` option parsing for the vendored library.

## Important APIs, Types, and Functions
Public functions are `fuse_opt_free_args`, `fuse_opt_add_arg`, `fuse_opt_insert_arg`, `fuse_opt_add_opt`, `fuse_opt_add_opt_escaped`, `fuse_opt_match`, and `fuse_opt_parse`. `fuse_opt_context` tracks input args, parsed output args, accumulated comma options, option templates, and callback state.

## Control Flow
Parsing copies argv[0], scans each argument, handles `-ofoo,bar` and `-o foo,bar` as option groups, honors `--`, matches templates from `struct fuse_opt`, writes values into offsets or calls the user callback, and reinserts accumulated options as `-o <opts>`. Option groups understand comma and backslash escaping. Template parameters support `%s` strings and integer `sscanf` formats.

## State and Persistence
No persistent state exists. The parser reallocates `fuse_args` ownership: on success, the caller receives a newly allocated argv array and the previous one is freed through the temporary context cleanup. Accumulated options are heap strings.

## Dependencies and Integration Points
This parser is used by `helper.cpp`, `mount_generic.h`, and `mount_bsd.h` to separate mount/helper/kernel options. It depends only on `fuse_opt.h` and libc allocation/string APIs.

## Risks
Ownership is subtle: callers must use `fuse_opt_free_args` on allocated outputs. `%s` option targets are overwritten without freeing previous values in `process_opt_param`, so templates should not match the same field repeatedly unless callers handle it. Escaping behavior must match mount helper expectations.

## Test Signals
Test non-option mountpoints, `--`, `-o` with escaped commas/backslashes, templates with `=` and separated space parameters, keep/discard/proc callback return values, multiple matches, allocation failures, and invalid integer parameters.
