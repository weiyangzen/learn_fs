# sources/user-network-fs/libfuse/include/fuse_opt.h

`fuse_opt.h` defines libfuse's reusable option parsing API. It parses command-line arguments and `-o` comma lists into application structs, callback decisions, and rewritten `fuse_args`.

`struct fuse_opt` describes a template, target offset, and value/key. `FUSE_OPT_KEY` and `FUSE_OPT_END` construct callback-only and sentinel entries. `struct fuse_args` owns argc/argv plus allocation state, initialized by `FUSE_ARGS_INIT`. Special keys are `FUSE_OPT_KEY_OPT`, `FUSE_OPT_KEY_NONOPT`, `FUSE_OPT_KEY_KEEP`, and `FUSE_OPT_KEY_DISCARD`. Public functions are `fuse_opt_parse`, `fuse_opt_add_opt`, `fuse_opt_add_opt_escaped`, `fuse_opt_add_arg`, `fuse_opt_insert_arg`, `fuse_opt_free_args`, and `fuse_opt_match`.

Control flow is template matching: matches set integer fields, allocate/replace string fields for formatted templates, or call `fuse_opt_proc_t`; unknown options and non-options also go to the callback. Return values decide whether arguments are retained, discarded, or fail parsing. Parser state lives in `struct fuse_args` and caller data; `%s` templates manage heap ownership at target fields.

Risks include offset/data layout mismatches, string ownership leaks or double-frees, accidentally dropping required mount options, and `-o` escaping edge cases. Test signals include exact matches, comma-list parsing, two-argument short options, formatted numeric/string writes, unknown and non-option callbacks, keep/discard keys, insertion before `--`, escaped commas, allocation failures, and cleanup.
