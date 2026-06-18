# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.c

Provides extended utilities for parameter dictionaries.

Key functions:
- `gs_param_string_eq`: compares `gs_param_string` to a C string by size and bytes.
- `param_put_enum`: reads a name parameter, matches against a null-terminated name table, stores enum index, and signals range/type errors.
- `param_put_bool`, `param_put_int`, `param_put_long`: convenience readers that propagate prior accumulated error code.
- `param_list_copy`: recursively copies all keys and values from one parameter list to another, including dictionaries/arrays.

Integration:
- Uses `gsparam.h` APIs and `gsparamx.h` declarations.
- Useful for device `put_params` implementations that collect multiple parameter validation errors.

Risk notes:
- `param_list_copy` uses fixed `char string_key[256]`; longer keys return rangecheck.
- `copy_persists` is set from allocator equality; the name suggests the condition may deserve careful review because persistence is modified based on allocator relationship.
