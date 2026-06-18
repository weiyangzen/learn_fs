# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.c

Purpose: provides general Ghostscript interpreter utilities for refs, packed arrays, object printing, operands, strings, operators, store checks, and matrices.

Major areas:
- Ref copying and initialization: `refcpy_to_old`, `refcpy_to_new`, and `refset_null_new`, including VM-space and save/undo handling.
- Equality: `obj_eq` implements PostScript-style equality across numeric integer/real pairs, name/string pairs, arrays, dictionaries, files, operators, save IDs, devices, structs, and font IDs; `obj_ident_eq` tightens string comparison to identity.
- String/name data: `obj_string_data`, `string_to_ref`, and `ref_to_string`.
- Printing: `obj_cvp` and `obj_cvs` implement `cvs`, `=`, `==`, and `===`-style conversion, including escaped strings, real-number formatting with required decimal points, operator names, type markers, and partial output via `start_pos`.
- Operators and arrays: `op_find_index`, `op_index_ref`, `array_get`, and `packed_get` convert operator indexes and unpack ordinary/mixed/short arrays.
- Store checks: `refs_check_space` enforces generation ordering when copying refs into non-local containers.
- Operand decoding: numeric, float, integer, real, and array-of-floats helpers validate stack/array operands.
- Matrix helpers: `read_matrix` and `write_matrix_in` convert six-element PostScript matrix arrays to/from `gs_matrix`, with save-aware writes.

Dependencies: name table, dictionary APIs, packed ref encoding, operator tables, stream string escaping, VM-space macros, matrix definitions, and interpreter memory/save macros.
