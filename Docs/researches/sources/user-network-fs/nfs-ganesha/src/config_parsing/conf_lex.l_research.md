# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_lex.l

## Purpose

`conf_lex.l` is the Flex scanner for Ganesha configuration files. It tokenizes the configuration language, handles `%include`, `%dir`, and `%url` directives, manages nested input buffers, and supplies typed tokens to the Bison grammar.

## Important APIs, Types, and Functions

Important scanner states are `YY_INIT`, `DEFINITION`, `TERM`, `INCLUDE`, `URL`, and `INCL_DIR`. Key helper functions are `ganeshun_yy_init_parser`, `ganeshun_yy_cleanup_parser`, `process_dir`, `new_file`, `fetch_url`, `pop_file`, and `ganeshun_yywrap`. `struct bufstack` tracks nested files/URLs.

## Control Flow

The scanner starts in `YY_INIT`, accepts top-level block identifiers, moves to `DEFINITION` for statements/blocks, and to `TERM` after `=` for typed values. `%include` pushes a single file, `%dir` opens matching regular files from a directory, and `%url` fetches a URL-backed stream through `config_url_fetch`. EOF pops the current buffer and resumes the previous file. Token rules classify quoted strings, booleans, arithmetic operators, numbers, FSIDs, IPv4/IPv6 addresses and CIDRs, netgroups, paths, plain tokens, and wildcard regex tokens.

## State and Persistence Behavior

The scanner maintains a buffer stack of open `FILE *` handles or URL memory streams, current filename, line number, config directory, file list, block depth, and parse generation. It records all parsed files in the config root and rejects repeated file paths to avoid include loops.

## Dependencies and Integration Points

It depends on Flex reentrant/bison-bridge APIs, `conf_yacc.h`, `analyse.h`, `conf_url.h`, Ganesha memory wrappers, logging, `dirent`, `fnmatch`, and `libgen`. The Bison parser consumes tokens through `ganesha_yylex`.

## Risks and Edge Cases

`process_dir` order follows directory iteration and is not sorted, so config load order can vary by filesystem. It only includes regular files based on `dirent.d_type`, which can be `DT_UNKNOWN` on some filesystems. Include-loop detection uses constructed path strings without canonicalization, so symlinks or path variants can bypass it. URL recursion can be compiled out only with `NO_URL_RECURSION`.

## Test Signals

Syntax tests should cover nested includes, duplicate includes, directory includes with glob patterns, URL includes, string escaping, IPv6/CIDR forms, FSIDs, wildcard clients, and scanner errors. Leak tests should cover parse failures while multiple buffers are stacked.
