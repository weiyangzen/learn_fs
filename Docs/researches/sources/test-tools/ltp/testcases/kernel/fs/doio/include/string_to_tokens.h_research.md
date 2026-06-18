# sources/test-tools/ltp/testcases/kernel/fs/doio/include/string_to_tokens.h

Purpose: `string_to_tokens.h` declares a small tokenization helper used by doio command-line parsing for comma-separated and colon-separated option subfields.

Important APIs and types: `string_to_tokens(char *arg_string, char **arg_array, int max_args, char *separator)` parses a string, stores token pointers in `arg_array`, and null-terminates the array. There are no exported structs or globals.

Control flow: the implementation uses `strtok()` according to the comment. That means parsing walks separators, replaces them with `'\0'`, and returns pointers into the original buffer.

State and persistence behavior: token state is stored by mutating the caller's input string. Because `strtok()` has hidden process-global parsing state, the helper is not reentrant or thread-safe unless the implementation avoids nested calls.

Dependencies and integration points: `doio.c` uses it in `parse_cmdline()` for `-M` memory allocation lists, in `parse_memalloc()` for `:`-separated allocation descriptors, and in `parse_delay()` for delay descriptors.

Risks: callers must pass mutable storage, not string literals. Nested tokenization can be fragile because `strtok()` keeps static state; the current doio use tokenizes one sub-string at a time but future nested use could break. The header does not define truncation behavior when token count exceeds `max_args`.

Test signals: useful checks include empty fields, repeated separators, maximum-token boundaries, different separator strings, mutation of input, and null termination of the output array.
