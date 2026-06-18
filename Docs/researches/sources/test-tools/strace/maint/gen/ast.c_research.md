# sources/test-tools/strace/maint/gen/ast.c

Purpose: allocation, interning, comparison, and freeing helpers for the generator DSL AST.

Important APIs/types/functions: `create_ast_node`, list/node constructors, `known_type`, `known_type_option`, `compare_type_option_list`, `ast_type_matching`, `create_or_get_type`, type-option constructors, and `free_ast_tree`.

Control flow: parser actions call constructors as grammar reductions occur. `create_or_get_type` checks the interned list before resolving a type through `resolve_type`; type options for numbers and nested types are also interned when possible. Matching supports template options for decoder selection. Freeing recursively releases AST nodes and selected owned strings/lists.

State and persistence behavior: process-local global intern tables `known_types` and `known_type_options` persist for the generator run. AST nodes store source locations using `cur_filename` and Bison locations. No file writes happen here.

Dependencies and integration points: used by `parse.y`, `lex.l`, `symbols.c`, `preprocess.c`, and `codegen.c`. Depends on `xmalloc` helpers and Bison `YYLTYPE`.

Risks: lifetime ownership is mixed: interned types and options are not comprehensively freed, acceptable for a short generator but relevant for tools/reuse. `free_ast_tree` does not deeply free all type structures. Template matching intentionally treats template IDs as wildcards only in matching mode.

Test signals: parser tests with duplicate declarations, nested types, template decoders, and malformed type options should produce expected ASTs or errors without crashes.
