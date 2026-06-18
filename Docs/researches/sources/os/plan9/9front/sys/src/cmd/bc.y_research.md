# File Research: sources/os/plan9/9front/sys/src/cmd/bc.y

This is the yacc grammar and translator for Plan 9 `bc`. It converts bc syntax into dc commands and either prints the generated dc program with `-c` or pipes it to `/bin/dc`.

Major responsibilities:
- Grammar for statements, expressions, assignments, loops, conditionals, function definitions, `auto`, `return`, `break`, `print`, base/scale settings, arrays, and increments/decrements.
- Emits dc command bundles using `bundle`, `routput`, `output`, and `conout`.
- Maintains function/local-variable save/restore prologues and epilogues through `pp` and `tp`.
- Implements lexer `yylex` with keyword recognition and comment/string scanning.
- Handles input from files first, then stdin.

Notable implementation details:
- Supports `-c`, `-d`, `-l`, and `-s`.
- `-l` prepends `/sys/lib/bclib`.
- Keyword detection checks two-letter prefixes and skips the rest of the word.
- Uses fixed workspaces: `cary[1000]`, `string[1000]`, `bspace[5000]`, branch label range starting at `crs=128`.

Risks and caveats:
- The translator is tightly bounded by fixed buffers and label limits.
- Comment scanning has an unbounded loop until `*/`.
- Error reporting emits dc code that prints diagnostics.
