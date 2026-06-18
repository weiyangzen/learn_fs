# sources/test-tools/strace/maint/gen/lex.l

Purpose: Flex lexer for the strace decoder-definition language.

Important APIs/types/functions: token rules for punctuation, decimal/hex/binary/character numbers, template identifiers like `$1`, identifiers including `@ret`, `%{...%}` decoder source blocks, `define`, `#ifdef`, `#ifndef`, `include`, `#endif`, comments, and `#import`. It uses import stack state, `cur_filename`, `cur_location`, `last_line_location`, and `update_yylloc`.

Control flow: normal lexing returns Bison tokens while tracking source coordinates. On `#import "file"` it saves lexer state, opens the imported file, pushes a buffer, and resumes from that file. EOF emits a synthetic newline once, then pops import state or terminates.

State and persistence behavior: maintains global current filename/location and a bounded import stack of 10 levels. It opens imported files but relies on buffer cleanup rather than explicit close in the visible code path.

Dependencies and integration points: consumed by Bison parser in `parse.y`; uses `xstrdup`, `yyerror`, and Bison semantic values.

Risks: import paths are used directly and nesting beyond 10 aborts. Identifier and decoder-source regexes encode DSL syntax tightly. Location tracking must remain synchronized with manual input consumption in import handling.

Test signals: parse definitions with imports, comments, template identifiers, binary/hex literals, `@ret`, and decoder blocks; error messages should point to the correct file/line/column.
