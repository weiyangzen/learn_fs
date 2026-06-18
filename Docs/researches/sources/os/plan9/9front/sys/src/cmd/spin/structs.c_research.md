# File Research: sources/os/plan9/9front/sys/src/cmd/spin/structs.c

`structs.c` implements PROMELA user-defined type and struct handling. It manages typedef registration, struct field expansion, runtime struct values, nested field lookup, code-generation traversal, and proctype-name registration.

Key responsibilities:
- Registers typedefs with `setuname`, lists them as C structs with `putunames`, and resolves names with `isutype`/`getuname`.
- Applies user-defined struct types to declared variables in `setutype`, preserving visibility flags and formal-parameter metadata.
- Initializes nested runtime struct values with `ini_struct`, copying template nodes with `cpnn` and assigning fresh channel IDs to copied channel fields.
- Resolves nested field references through `do_same`.
- Reads and writes nested struct fields with `Rval_struct` and `Lval_struct`.
- Counts flattened field slots with `Cnt_flds`, returns terminal field type with `Sym_typ`, and fills type-width arrays with `Width_set`.
- Builds printable/generated names for nested fields through `full_name` and `struct_name`.
- Validates field references with `validref`.
- Traverses struct fields for channel cases, generic variable generation, C code generation, and runtime dumping with `walk2_struct`, `walk_struct`, `c_struct`, and `dump_struct`.
- Expands implicit structure references into comma-linked explicit field references with `expand`, `mk_explicit`, and `retrieve`.
- Maintains known proctype names through `setpname`/`isproctype`.

Important interactions:
- Parser actions call `setutype`, `expand`, and `mk_explicit` for declarations, message parameters, receive arguments, and formal parameters.
- Runtime value access from `sched.c`/`vars.c` delegates to `Rval_struct` and `Lval_struct`.
- Code-generation modules call traversal functions to emit state-vector and C representations.

Notable details:
- Struct arrays are supported, but arrays of structures in parameter lists are explicitly rejected.
- `owner` is global parser state used to distinguish struct-field symbols during declaration and lookup.
- There is a duplicated `if (m->ntyp == ',')` and duplicated loop header in `retrieve`; both appear redundant.
