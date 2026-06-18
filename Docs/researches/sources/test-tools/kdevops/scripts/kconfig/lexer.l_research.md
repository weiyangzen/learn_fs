# sources/test-tools/kdevops/scripts/kconfig/lexer.l

## Purpose
This Flex lexer tokenizes Kconfig files, handles quoted strings, assignment values, help text indentation, variable expansion, and nested `source` inclusions.

## Important APIs, Types, And Functions
The generated scanner exposes `yylex()`. Internal helpers include `new_string()`, `append_string()`, `alloc_string()`, `warn_ignored_character()`, `expand_token()`, `append_expanded_string()`, `zconf_starthelp()`, `zconf_endhelp()`, `zconf_fopen()`, `zconf_initscan()`, `zconf_nextfile()`, and `zconf_endfile()`. `struct buffer` stores nested scanner state. Start conditions are `ASSIGN_VAL`, `HELP`, and `STRING`.

## Control Flow
The first-stage lexer recognizes Kconfig keywords, operators, comments, whitespace, bare words, expandable `$` words, quoted strings, assignment-value lines, and help blocks. `yylex()` is a second-stage wrapper that suppresses repeated blank-line tokens, updates parser line numbers at statement starts, and switches to `ASSIGN_VAL` after top-level assignment operators. Includes push the current Flex buffer onto a parent stack, open the next file, detect recursive inclusion, and restore the previous buffer at EOF.

## State And Persistence
Global scanner state includes `cur_filename`, `cur_lineno`, previous token tracking, dynamic `text` buffer, current buffer stack, and help indentation counters. It reads Kconfig source files, including paths relative to `srctree`, and writes only diagnostics.

## Dependencies And Integration Points
It depends on Flex, `parser.tab.h`, `lkc.h`, `preprocess.h`, and `xalloc`. The parser calls `zconf_initscan()` and consumes tokens from `yylex()`.

## Risks And Test Signals
String and variable expansion push unused characters back into the scanner, so boundary cases around `$`, quotes, and assignments need coverage. Help indentation handling is sensitive to tabs and blank lines. Recursive include detection compares filenames as passed, so different path spellings could evade it. Tests should parse nested sources, assignments, variable expansions, multiline strings, help text, missing newline EOF, and recursive inclusion.
