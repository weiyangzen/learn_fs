# sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c

Purpose: C fixture for testing extraction of global variables, static file-local variables, macro-defined globals, and a simple function.

Important APIs/types/functions: Defines `DEFINE_VAR`, `DEFINE_STATIC_VAR`, `macro_var`, `static_macro_var`, `global_var`, `local_to_file_var`, and `some_function`.

Control flow: There is no runtime control flow beyond `some_function` assigning and discarding a local variable. The fixture exists to drive clang AST/database extraction.

State and persistence behavior: Declares initialized globals and statics in source form only. The resulting persisted state is represented in `global_vars.c.json`.

Dependencies/integration points: Consumed by `tooltest.TestClangTool` and codesearch golden tests. It validates that macro expansions and static attributes are reflected in the database.

Risks: Very small fixture; changes to line numbers or macro shape require updating the golden JSON.

Test signals: Expected definitions are captured in `global_vars.c.json`, including `is_static` on static variables.
