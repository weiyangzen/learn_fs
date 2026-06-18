# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iref.h

Core Ghostscript interpreter object-reference definition header. It defines `ref`, object types, type/attribute bit layout, type-property tables, debug/type strings, pointer/value union fields, and common ref inspection/manipulation macros.

Key contents:
- Defines `ref` and opaque packed refs (`ref_packed`).
- Defines the `ref_type` enum: invalid, boolean, dictionary, file, array variants, struct/astruct, fontID, integer, mark, name, null, operator, real, save, string, device, oparray, and `t_next_index`.
- Documents which types are composite, executable-sensitive, access-protected, and size-bearing.
- Defines array and struct type spans used by fast type tests.
- Defines type-property flags and `REF_TYPE_PROPERTIES_DATA`.
- Defines debug/type/print string tables for diagnostics and PostScript type names.
- Defines location attributes (`l_mark`, `l_new`), VM-space bit placement, access bits (`a_write`, `a_read`, `a_execute`), `a_readonly`, `a_all`, executable bit, and type bit placement.
- Defines `REF_ATTR_PRINT_MASKS` for debug printing.
- Forward-declares interpreter object support types such as `dict`, `name`, `stream`, `gx_device`, and `obj_header_t`.
- Defines `op_proc_t`.
- Defines the concrete `ref_s` layout: a `tas_s` header containing `type_attrs` and `rsize`, plus a union for integer, bool, real, save id, byte pointers, ref pointers, names, dictionaries, packed refs, operator procs, files, devices, and structures.
- Provides fast macros for size access, type access, base type conversion, array/procedure/struct checks, type/attribute setting, interpreter dispatch key generation, attribute tests, attribute mutation, and struct pointer access.
- Defines `empty_ref_data`, `arch_sizeof_ref`, `arch_align_ref_mod`, `max_array_size`, and `max_string_size`.

Notable dependencies:
- Relies on architecture macros such as `arch_is_big_endian`, `arch_align_*`, and `arch_log2_sizeof_short`.
- Used by nearly every interpreter component through `ghost.h` and related headers.
- Closely related to `ipacked.h`, `store.h`, GC code, and the main interpreter dispatch in `interp.c`.

Research notes:
- The first field of `ref` must remain `type_attrs` because packed arrays and interpreter dispatch depend on the first two bytes being distinguishable from `ref_packed`.
- Types beyond `t_next_index` are reserved for interpreter pseudo-types used to speed high-frequency operators.
- Adding a new type requires coordinated updates in type string tables, initialization PostScript, debug printing, GC dispatch, interpreter dispatch, object conversion/equality code, and restore checks.
- The dispatch macro `r_type_xe` deliberately casts through a less-strictly-aligned type because the interpreter may point it at packed refs.
