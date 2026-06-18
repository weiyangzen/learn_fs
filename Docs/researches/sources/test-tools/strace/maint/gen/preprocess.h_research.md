# sources/test-tools/strace/maint/gen/preprocess.h

Purpose: declares the intermediate representation passed from AST preprocessing to code generation.

Important APIs/types/functions: `statement_condition`, `preprocessor_statement`, `preprocessor_statement_list`, `struct_def`, `syscall_argument`, `decoder`, `decoder_list`, `syscall`, `syscall_group`, `processed_ast`, and `preprocess`.

Control flow: not executable; defines how conditional wrappers, syscall definitions, decoder templates, and variant trees are represented.

State and persistence behavior: structures use flexible arrays for condition values and syscall arguments, with allocation performed by `preprocess.c`.

Dependencies and integration points: included by `deflang.h` and `codegen.c`; all generated decoder behavior depends on this IR's fields.

Risks: ownership and lifetime are implicit. `struct_def` is present but marked TODO, so struct statements are not fully represented beyond symbol/type lookup.

Test signals: compile-time compatibility plus generated decoder output for conditional and variant definitions validates the IR.
