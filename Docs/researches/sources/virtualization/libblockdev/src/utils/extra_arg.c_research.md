# File Research: sources/virtualization/libblockdev/src/utils/extra_arg.c

This file implements the boxed `BDExtraArg` helper used to pass command-line extra arguments through libblockdev APIs.

Functions:
- `bd_extra_arg_copy()` deep-copies `opt` and `val`.
- `bd_extra_arg_free()` frees owned strings and the struct.
- `bd_extra_arg_list_free()` frees a NULL-terminated vector of `BDExtraArg*`.
- `bd_extra_arg_get_type()` registers `BDExtraArg` as a boxed GObject type.
- `bd_extra_arg_new()` constructs a new extra arg, storing empty strings for NULL option/value inputs.

Research relevance:
- This boxed type is exposed to GI/Python and consumed by `exec.c`’s `_append_extra_args()`.
- It models option and value separately, allowing options without parameters by using empty or NULL values.
