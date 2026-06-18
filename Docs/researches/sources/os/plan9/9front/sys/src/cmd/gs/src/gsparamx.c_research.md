# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.c

Implements extended parameter-list utilities.

Main behavior:
- `gs_param_string_eq` compares `gs_param_string` with a C string.
- `param_put_enum` reads a name and maps it through a null-terminated enum-name table.
- `param_put_bool`, `param_put_int`, and `param_put_long` read typed values while accumulating and signaling errors.
- `param_list_copy` recursively copies one parameter list to another, including nested collections.

Important details:
- Preserves key persistence state while copying.
- Treats aggregate persistence carefully depending on whether source and destination use the same allocator.
- Handles dictionaries, integer-key dictionaries, and arrays recursively.
