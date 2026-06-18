# sources/security-integrity/selinux/libsemanage/src/conf-scan.l

Purpose: flex lexer for `semanage.conf`. It recognizes option names, command block headers, assignment delimiters, and string arguments for the bison parser.

Important APIs/types/functions: returns tokens such as `MODULE_STORE`, `STORE_ROOT`, `COMPILER_DIR`, `VERSION`, `LOAD_POLICY_START`, `SETFILES_START`, verifier starts, `PROG_PATH`, `PROG_ARGS`, `BLOCK_END`, and `ARG`. Helpers `my_strdup` and `my_qstrdup` duplicate unquoted and quoted arguments.

Control flow: comments and whitespace are ignored. Seeing `=` switches to an `arg` start condition so the rest of the value line is captured as one argument, with quoted empty strings represented as NULL.

State and persistence behavior: lexer state is generated flex state plus allocated `ARG` strings passed to parser actions, which are responsible for freeing them. It does not persist configuration itself.

Dependencies and integration points: includes generated `conf-parse.h`; compiled by `src/Makefile` before the parser object; consumed exclusively by `conf-parse.y`.

Risks: unquoted argument trimming mutates the matched buffer before duplicating; quoted values do not trim internal whitespace. Test signals include quoted empty values, comments, unknown characters, all recognized option tokens, and scanner destruction after parsing.
