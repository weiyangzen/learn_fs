# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.c

Interpreter debug support, forcibly compiled with `DEBUG`. It prints names, refs, packed refs, ref memory regions, stacks, and arrays.

Capabilities:
- `debug_print_name` / `debug_print_name_index`
- Full ref printing for arrays, dictionaries, files, fonts, names, operators, packed arrays, strings, structs, etc.
- Packed-ref decoding for packed operators, ints, literal/executable names.
- `debug_dump_one_ref`, `debug_dump_refs`, `debug_dump_stack`, `debug_dump_array`

It depends on type-name and attribute-print macro tables from ref definitions. This file is diagnostic-only.
