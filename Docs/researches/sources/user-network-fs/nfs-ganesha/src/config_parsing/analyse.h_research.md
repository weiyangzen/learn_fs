# sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.h

## Purpose

`analyse.h` declares the private parse tree, token table, file-list, parse-root, and parser-state structures shared by the scanner, parser, analysis code, and semantic config loader.

## Important APIs, Types, and Functions

Key types are `enum node_type`, `struct config_node`, `struct file_list`, `struct token_tab`, `struct config_root`, and `struct parser_state`. Declared functions include `save_token`, `ganesha_yyparse`, `ganeshun_yy_init_parser`, `ganeshun_yy_cleanup_parser`, `token_compare_hash`, `config_error`, `print_parse_tree`, and `free_parse_tree`.

## Control Flow

The scanner stores recognized tokens in `config_node` terminals and uses `parser_state` to track current scanner, include buffer stack, current file, block depth, and error sink. The parser builds `TYPE_BLOCK`, `TYPE_STMT`, and `TYPE_TERM` nodes under a `TYPE_ROOT`. Later semantic loading walks those lists.

## State and Persistence Behavior

`config_root` owns parse-tree memory, the initial config directory, included file list, generation number, and token-tree initialization flag. `config_node` stores filename pointers into the file list and token pointers into the intern table, so cleanup order matters.

## Dependencies and Integration Points

It depends on `gsh_list.h`, `avltree.h`, `city.h`, and public config term types from `config_parsing.h`. It is included by generated grammar/lexer sources and by `config_parsing.c`.

## Risks and Edge Cases

Because the structures are private but shared among generated files, changes require regenerating and recompiling the parser. `filename` and token strings are non-owning references, so consumers must not outlive the parse tree. The global token-tree implementation behind these declarations limits concurrency unless externally serialized.

## Test Signals

Compile tests for generated parser/scanner and semantic loader catch type drift. Runtime parse/free tests with includes and URL-backed configs validate ownership expectations.
