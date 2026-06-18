# sources/test-tools/strace/maint/gen/symbols.c

Purpose: symbol table and type resolver for the generator DSL.

Important APIs/types/functions: linked-list `symbol_entry`, global `symbol_table`, `symbol_get`, `symbol_add`, and `resolve_type`. `resolve_type` recognizes special types `const`, `ptr`, `ref`, `xor_flags`, and `or_flags`, validates option counts/kinds, and fills `struct ast_type`.

Control flow: parser actions add named declarations to catch duplicates. Type construction calls `resolve_type`, which starts every type as `TYPE_BASIC`, then rewrites the union fields for special names after validating options.

State and persistence behavior: symbol table is process-global for one generator run. Types are returned through caller-provided storage and may reference option/type nodes interned elsewhere.

Dependencies and integration points: called by `ast.c` and `parse.y`; `codegen.c` relies on resolved type tags to choose printers and dispatch behavior.

Risks: some error strings mention the wrong type name (`len`/`ptr`) in messages. Template identifiers are rejected as ordinary options here, while template-aware matching is handled elsewhere. No cleanup of symbol table entries is visible.

Test signals: invalid `ptr` direction, wrong option counts, duplicate symbols, and flag/ref types should produce deterministic parser errors.
