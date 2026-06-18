# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_yacc.y

## Purpose

`conf_yacc.y` is the Bison grammar for Ganesha configuration files. It builds the parse tree consumed by semantic config loading.

## Important APIs, Types, and Functions

Generated/parser-facing functions and helpers include `ganesha_yyparse`, `ganesha_yylex`, `config_parse_error`, `ganesha_yyerror`, `config_block`, `config_stmt`, `config_term`, `link_sibling`, `link_node`, `dump_all_blocks`, and global `all_blocks`. Grammar values are token strings and `struct config_node *`.

## Control Flow

The grammar accepts a `deflist` of definitions. A definition is either `IDENTIFIER = statement` or `IDENTIFIER { block }`. Statements are semicolon-terminated comma-separated expression lists. Expressions map scanner tokens into typed term nodes, preserving arithmetic opcodes for signed/complement numeric forms. Blocks and statements allocate nodes, attach child lists, and update parent pointers. Syntax errors in statements or blocks are reported and recovered at `;` or `}`.

## State and Persistence Behavior

The parser mutates the `config_root` tree in `parser_state` and appends every block node to global `all_blocks` for later name lookup. Nodes store non-owning token and filename pointers managed by the parse root.

## Dependencies and Integration Points

It depends on Bison pure parser mode, location tracking, the Flex scanner, `analyse.h`, `config_parsing.h`, Ganesha list/memory/log APIs, and term type definitions. `config_parsing.c` later loads typed structures from the tree.

## Risks and Edge Cases

Empty configuration files are reported but can still produce a parse root. `all_blocks` is global, so concurrent parses or multiple live parse trees need external discipline. `parse_block` in `config_parsing.c` relies on node names and statement values built here. Error recovery drops malformed subtrees, which can lead to later missing/unknown parameter diagnostics.

## Test Signals

Grammar tests should cover empty files, top-level blocks, nested blocks, empty blocks/statements, multiple expression values, arithmetic numeric forms, syntax recovery, and parent linkage through `get_parse_root`.
