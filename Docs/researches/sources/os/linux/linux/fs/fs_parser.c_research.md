# File Research: sources/os/linux/linux/fs/fs_parser.c

## Purpose
This file implements generic filesystem mount/reconfiguration parameter parsing for the modern `fs_context` mount API. Filesystems describe supported parameters with `struct fs_parameter_spec`; this parser matches keys, handles `no`-prefixed negation for flags, converts string values into typed parse results, and reports errors through the filesystem context log.

## Main Definitions
- `bool_names[]` accepts `0`, `1`, `false`, `no`, `true`, and `yes`.
- `lookup_constant()` and `__lookup_constant()` search simple name/value tables.
- `fs_lookup_key()` matches `struct fs_parameter` keys against a parameter description table and handles `fs_param_neg_with_no`.
- `__fs_parse()` is the central parser: match key, warn for deprecated parameters, convert values, and return the option id.
- `fs_lookup_param()` turns a string or filename parameter into a resolved `struct path`, with optional block-device validation.
- Type validators include `fs_param_is_bool`, `fs_param_is_u32`, `fs_param_is_s32`, `fs_param_is_u64`, `fs_param_is_enum`, `fs_param_is_string`, `fs_param_is_fd`, `fs_param_is_file_or_string`, `fs_param_is_uid`, `fs_param_is_gid`, and `fs_param_is_blockdev`.
- Under `CONFIG_VALIDATE_FS_PARSER`, `fs_validate_description()` detects duplicate parameter names of the same flag/non-flag kind.

## Control Flow And Behavior
`__fs_parse()` zeroes `result->uint_64`, finds a matching spec, emits a deprecation warning when needed, and then either handles a flag directly or calls the spec’s type conversion callback. Unknown keys return `-ENOPARAM`; mismatched or invalid values usually return `-EINVAL` through the `inval_plog()` logging path.

`fs_lookup_key()` distinguishes flags from value parameters, so the same name can exist once as a flag and once as a valued parameter. For flag input, it also recognizes `nofoo` as a negated form of `foo` only when the spec opted into `fs_param_neg_with_no`.

`fs_lookup_param()` accepts either `fs_value_is_string` or `fs_value_is_filename`. Strings are wrapped with `getname_kernel()` and looked up from `AT_FDCWD`; filename parameters preserve their provided `dirfd`. If `want_bdev` is true, the resolved path must be a block device or the function returns `-ENOTBLK`.

## Dependencies And Interfaces
This file is used by filesystem `fs_context` implementations and exported parser helpers. It depends on `fs_context`, `fs_parser`, name lookup, security/user namespace conversion, and internal VFS logging helpers.

## Concurrency And Safety
The parser itself is synchronous and does not keep global mutable state. Path lookup and user namespace ID conversion rely on standard VFS and namespace helpers. Empty values are rejected unless the spec has `fs_param_can_be_empty`.

## Research Notes
This is shared mount API infrastructure. Important semantic details are: flag negation is opt-in, unknown parameter behavior is controlled by higher-level description policy, UID/GID parsing validates against `current_user_ns()`, and fd parameters reject values larger than `INT_MAX`.
