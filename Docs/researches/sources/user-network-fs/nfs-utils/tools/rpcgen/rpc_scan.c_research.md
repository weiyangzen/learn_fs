<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.c

## Purpose

`rpc_scan.c` is rpcgen's lexical scanner. It reads preprocessed RPCL input, skips whitespace/comments, preserves `%` directives into output, tracks `#line` information, and returns tokens to the parser.

## Important APIs, Types, and Functions

Public scanner functions are `scan`, `scan2`, `scan3`, `scan_num`, `peek`, `peekscan`, and `get_token`. Internal helpers include `unget_token`, `findstrconst`, `findchrconst`, `findconst`, `findkind`, `cppline`, `directive`, `printdirective`, and `docppline`. The `symbols` table maps reserved words to token kinds.

## Control Flow

`get_token` first returns a pushed token if present, otherwise reads lines from global `fin`, updates `linenum`, processes cpp line markers and `%` output directives, skips whitespace and C block comments, then recognizes punctuation, string/char constants, numeric constants, identifiers, or reserved keywords. Parser wrappers enforce expected tokens and delegate error reporting.

## State and Persistence Behavior

Scanner state is global: `curline`, `where`, `linenum`, `infilename`, and one-token pushback state. It writes passthrough directives to `fout`. It persists no files directly.

## Dependencies and Integration Points

It depends on preprocessed input from `rpc_main.c`, error helpers from `rpc_util.c`, gettext macros, and token/AST headers. It feeds `rpc_parse.c`.

## Risks and Edge Cases

Comment state is local to one `get_token` call and still handles multiline comments through the internal read loop, but scanner recovery is minimal. String and char constant parsing does not process escapes deeply and char constants require exactly three bytes including quotes. Numeric constants are returned as identifiers. Illegal characters abort generation and cleanup outputs.

## Test Signals

Scanner tests should cover comments across lines, `%` directives, cpp line markers, identifiers adjacent to keywords, hex/decimal constants, negative constants, strings, invalid/unterminated strings, char constants, pushback, and parser expectation errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.c -->
