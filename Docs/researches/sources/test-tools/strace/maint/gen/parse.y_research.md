# sources/test-tools/strace/maint/gen/parse.y

Purpose: Bison grammar and main program for the decoder-definition generator.

Important APIs/types/functions: grammar productions for compound statements, syscalls, typed arguments, return types, type option lists/ranges/templates, defines, includes, conditionals, structs, flags, and decoder source blocks. Helper `error_prev_decl`, formatted `yyerror`, and `main` are defined here.

Control flow: `main` validates input/output arguments, initializes the lexer, runs `yyparse`, preprocesses the root AST, calls `generate_code`, and frees the AST. Grammar actions construct AST nodes and insert named syscalls/structs/flags into the symbol table, rejecting duplicate declarations.

State and persistence behavior: uses static `root`, Bison error count/location state, lexer globals, and symbol table state. Writes only through `generate_code`.

Dependencies and integration points: tied to `lex.l` token stream, `ast.c` constructors, `symbols.c` duplicate detection, `preprocess.c`, and `codegen.c`.

Risks: error recovery can continue through malformed lines but may leave partial AST state. Some grammar productions accept attributes but ignore them (`syscall_attribute`, `struct_attr`), so future syntax assumptions need care.

Test signals: invalid duplicate declarations should produce previous-location errors; malformed type options should print source context; existing `.def` files should parse and generate compilable C.
