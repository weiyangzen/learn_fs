# sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.c

## Purpose

`analyse.c` owns token interning, parse-tree display, parse-tree cleanup, and low-level config error formatting for the generated lexer/parser subsystem.

## Important APIs, Types, and Functions

Important functions are `sanitize_token_str`, `save_token`, `config_term_name`, `config_term_desc`, `print_parse_tree`, `free_parse_tree`, and `config_error`. Internal helpers include AVL token comparison/lookup, recursive `print_node`, `print_token_tree`, `free_node`, and `free_token_tree`.

## Control Flow

Scanner tokens flow through `save_token`. Quoted tokens are optionally sanitized in place, hashed with `CityHash64`, looked up in a static AVL tree, and either deduplicated or allocated as a new `token_tab`. Parse-tree printing emits a summary, file list, token table, and recursive block/statement/term structure. Cleanup recursively unlinks/free nodes, frees file-list paths, frees the token AVL tree, and frees the root. Errors are formatted into a stream with a form-feed separator and optionally mirrored to full-debug logs.

## State and Persistence Behavior

The token table is a static AVL tree shared by the parser implementation and guarded only by the current parse-root initialization flag. Tokens are persisted for the lifetime of a `config_root`; parse nodes reference interned token strings instead of owning them. `config_root` owns the file list, config directory, generation value, and parse tree.

## Dependencies and Integration Points

It depends on `analyse.h`, `config_parsing.h`, `gsh_list`, `avltree`, `CityHash64`, Ganesha memory wrappers, and logging globals. The generated scanner calls `save_token`, the parser creates nodes that store token pointers, and `config_parsing.c` consumes the tree.

## Risks and Edge Cases

The static token tree can be problematic if multiple parse trees are live or parsed concurrently; cleanup frees the static tree without resetting the static root. `config_error` uses `vsprintf` into a fixed `LOG_BUFF_LEN` buffer, so very long diagnostics can overflow unless upstream formatting bounds them. `sanitize_token_str` mutates scanner text, which is expected but should not be reused afterward.

## Test Signals

Parser tests should include repeated tokens to verify interning, quoted strings with escapes, parse tree print/free under valgrind or sanitizers, and malformed input producing separated diagnostics. Concurrent reload tests would expose token-tree global-state hazards.
