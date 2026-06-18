# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iref.h

Core Ghostscript object reference representation and type/attribute macro definitions.

Key behavior:
- Forwards `ref` and defines opaque `ref_packed`.
- Defines PostScript/interpreter object types including scalar types, dictionaries, files, arrays, packed arrays, structs, names, operators, strings, devices, and op arrays.
- Documents which types are composite, executable-sensitive, access-controlled, and size-bearing.
- Defines type property tables and type-name string tables for debugging, `type`, and printing.
- Defines location attributes (`l_mark`, `l_new`), VM-space bits, access bits, executable bit, and type-bit layout.
- Defines debug attribute print masks.
- Forwards abstract runtime types such as `dict`, `name`, `stream`, `gx_device`, and `obj_header_t`.
- Defines `op_proc_t`.
- Defines `struct ref_s`, with `tas.type_attrs`, `tas.rsize`, and a union for integer, bool, real, save id, byte/string pointers, ref arrays, packed arrays, operators, streams, devices, dictionaries, names, and structs.
- Provides macros for size access, type access, base type normalization, array/procedure/struct tests, structure type tests, type/attribute mutation, fast interpreter `type_xe` dispatch, attribute tests/mutation, and struct pointer access.
- Defines empty ref data, ref size/alignment requirements, maximum array size, and maximum string size.

Research notes:
- The first field layout is constrained by packed-array decoding in `ipacked.h` and `interp.c`.
- Extended pseudo-types starting at `t_next_index` encode high-frequency operators for dispatch speed; `r_btype` maps them back to `t_operator`.
- Comments list every subsystem that must be updated when adding new ref types.
