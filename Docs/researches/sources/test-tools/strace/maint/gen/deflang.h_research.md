# sources/test-tools/strace/maint/gen/deflang.h

Purpose: shared declarations for the generator's lexer, parser, preprocessor, and code generator.

Important APIs/types/functions: declares external `yyin`, `last_line_location`, `cur_filename`, `lexer_init_newfile`, formatted `yyerror`, and `generate_code`. Includes `preprocess.h` and `xmalloc.h`.

Control flow: not executable itself; it provides the cross-module contract used by generated Bison/Flex code and handwritten generator C.

State and persistence behavior: exposes lexer/parser globals for current file and error-position tracking.

Dependencies and integration points: central include for `lex.l`, `parse.y`, `ast.c`, `symbols.c`, `preprocess.c`, and `codegen.c`.

Risks: global variables make the generator single-threaded and require careful reset between imported files or repeated parses.

Test signals: successful Flex/Bison compilation and useful syntax-error locations validate this header's declarations.
