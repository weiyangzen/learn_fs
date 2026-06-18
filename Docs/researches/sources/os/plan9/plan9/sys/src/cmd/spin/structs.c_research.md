# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/structs.c

This file implements Promela user-defined structure type handling, proctype-name tracking for lexer disambiguation, struct field expansion, runtime struct value access, and generated-code helpers for structs.

Type registries:
- `Unames` stores typedef/user type definitions.
- `Pnames` stores known proctype names so the lexer can return `PNAME`.
- Global `owner` tracks the typedef or struct-owner context during parsing.

User type functions:
- `setuname()` registers a new typedef body under `owner`.
- `putunames()` emits C `struct` definitions for all user-defined types.
- `isutype()` and `getuname()` query typedef names.
- `setutype()` applies a user type to declared variables, setting `STRUCT`, template list, defining type name, visibility bits, formal parameter flags, and array sanity checks.

Runtime access:
- `ini_struct()` lazily initializes a struct symbol’s `Sval` array by deep-copying the typedef template and initializing nested fields.
- `do_same()` locates the requested subfield for a struct reference and performs index checking.
- `Rval_struct()` recursively reads nested struct fields and casts values.
- `Lval_struct()` recursively writes nested struct fields and updates `setat`.
- `Sym_typ()` resolves the leaf type for explicit struct field references.

Expansion and naming:
- `Cnt_flds()` counts flattened non-struct fields.
- `Width_set()` fills message field-width arrays for struct-valued message parameters.
- `mk_explicit()` expands implicit struct references into comma lists of explicit field references.
- `expand()` applies that expansion to declaration/reference lists when allowed.
- `retrieve()` reconstructs an explicit field reference for a flattened index.
- `full_name()` and `struct_name()` print or build dotted field names.

Generated-code and diagnostics:
- `walk2_struct()` visits nested structs to handle channel cases.
- `walk_struct()` and `c_struct()` emit generated variable/state-vector handling for nested fields.
- `dump_struct()` prints runtime struct contents, using `doq()` for channels and `sr_mesg()` for scalar values.
- `validref()` checks that a referenced field exists in a structure.
- `setpname()` and `isproctype()` maintain proctype name recognition.

Risk notes:
- Struct templates are copied by manually duplicating `Lextok` and `Symbol` objects in `cpnn()`.
- Error handling is mostly fatal/non-fatal parser diagnostics, not recoverable API results.
- Some generated name buffers are fixed-size and assume reasonable nesting/name lengths.
