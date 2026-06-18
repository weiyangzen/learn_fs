# sources/user-network-fs/libfuse/lib/fuse_opt.c

Purpose: `fuse_opt.c` implements libfuse's argument and `-o` option parsing framework around `struct fuse_args`, `struct fuse_opt`, and optional callback processors. It is the shared parser used by low-level session options, high-level helper options, mount options, modules, and connection capability options.

Important APIs, types, and functions: Public APIs are `fuse_opt_free_args`, `fuse_opt_add_arg`, `fuse_opt_insert_arg`, `fuse_opt_add_opt`, `fuse_opt_add_opt_escaped`, `fuse_opt_match`, and `fuse_opt_parse`. Internal `struct fuse_opt_context` tracks input argv, output argv, accumulated `-o` options, parser callback, non-option boundary, and user data. Template handling is implemented by `match_template`, `find_opt`, `process_opt_param`, `process_opt`, `process_opt_sep_arg`, `process_gopt`, and option-group splitting helpers.

Control flow: `fuse_opt_parse` initializes a context, preserves `argv[0]`, iterates arguments, splits `-ofoo,bar` and `-o foo,bar` groups, handles `--`, matches each option against templates, writes integer/string values to `data + offset`, or calls the user callback with `FUSE_OPT_KEY_*`. Kept unknown options are copied to output argv or escaped back into a rebuilt `-o` string. On success it swaps parsed output into the caller's `struct fuse_args` and frees the old vector.

State and persistence behavior: The parser creates a new allocated argv vector and may consume/free the old vector if `args->allocated` is set. String options replace prior values at their target offset. The parser does not persist global state; all state is per-parse and freed before return.

Dependencies and integration points: It depends on `fuse_i.h`, `fuse_opt.h`, and `fuse_misc.h`. It is used by `helper.c`, `fuse_lowlevel.c`, mount option parsing, and runtime modules such as `iconv` and `subdir`. Template semantics are part of libfuse's public API, so downstream filesystems can provide their own `struct fuse_opt` tables and callbacks.

Risks: Offset-based writes assume the option table matches the target data struct; a wrong offset or `%` format corrupts memory. Escaping and octal decoding in option groups are easy to regress. `process_opt` has subtle handling for templates with separators and separate arguments. Memory ownership is strict: callers must understand when argv strings are duplicated, transferred, or freed.

Test signals: Parser tests should cover exact matches, `key` callbacks, discard/keep behavior, `-o` comma groups, escaped commas/backslashes/octal escapes, separate-argument templates, `--`, invalid numeric formats, missing arguments, string replacement, and non-allocated input argv preservation.
