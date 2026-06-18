# File Research: sources/os/plan9/9front/sys/src/cmd/awk/re.c

Provides awk’s interface to the Plan 9 regular-expression engine.

Key responsibilities:
- Preprocesses awk regex syntax into forms accepted by Plan 9 `regexp`.
- Handles special conversions for empty groups/classes, literal hyphens in classes, hex/octal escapes, and common escaped characters.
- Compiles regex patterns with `regcomp`.
- Maintains a small runtime cache of dynamic regex programs with use and in-use counters.
- Exposes match functions for boolean match, positioned match, and non-empty match.
- Updates global `patbeg` and `patlen` for functions such as `match`, `sub`, `gsub`, and field splitting.
- Provides `regerror` and `overflow` fatal handlers.

Important interfaces:
- Exports `compre`, `releasere`, `match`, `pmatch`, `nematch`, `hexstr`, and `quoted`.
- Uses Plan 9 `regexp.h` `Reprog`, `Resub`, `regcomp`, and `regexec`.

Notes:
- Cache is only used at runtime (`compile_time == 0`), not while compiling the awk program.
- `MAXRE` limits preprocessed regex size to 512 bytes.
