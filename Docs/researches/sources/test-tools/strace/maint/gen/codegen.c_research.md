# sources/test-tools/strace/maint/gen/codegen.c

Purpose: converts the preprocessed generator AST into C decoder functions that use strace's syscall-printing APIs.

Important APIs/types/functions: type mapping arrays, decoder list, output helpers, `type_to_ctype`, `type_variable_declaration`, `get_sys_func_return_flags`, `resolve_type_option_to_value`, pointer/value printers, `generate_templated_printer`, `generate_printer`, `generate_return_flags`, `generate_decoder`, `output_defines`, `output_variant_syscall_group`, `output_syscall_groups`, and `generate_code`.

Control flow: `generate_code` opens the output file, writes headers/includes, stores decoder templates, emits preprocessor statements, and recursively emits syscall groups. For each syscall it chooses an entry/exit printing strategy based on out-pointer count, prints arguments using explicit or inferred decoders, handles variants by dispatching on `const` arguments, and returns appropriate `RVAL_*` flags.

State and persistence behavior: writes generated C output. Runtime state during generated decoder execution can use `set_tcb_priv_data` for inout pointer snapshots. Codegen itself stores decoder templates in a static pointer and emits warnings to stderr.

Dependencies and integration points: depends on `processed_ast` from `preprocess.c`, symbols from `ast.c`, strace C helper APIs such as `tprints_arg_name`, `umove_or_printaddr`, `printflags64`, `printxval64`, `RVAL_DECODED`, and generated DSL definitions.

Risks: more than one out pointer is currently emitted as `#error TODO`, so DSL inputs must avoid that shape. `store_single_value` copies `tmp_var` using `memcpy(tmp_buffer, tmp_var, sizeof(tmp_var))`, which is subtle for arrays/pointers. Template substitution has fixed stack/substitution arrays and warnings for unresolved refs rather than hard failures.

Test signals: generated C should compile without `#error` for all checked-in definitions, and decoder output tests should verify variant dispatch, pointer directions, flag printers, and return-value formatting.
