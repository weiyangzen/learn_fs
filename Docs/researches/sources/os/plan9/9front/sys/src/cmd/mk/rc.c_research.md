# File Research: sources/os/plan9/9front/sys/src/cmd/mk/rc.c

Contains rc-shell-specific quoting, token scanning, and shell-name parsing.

Key behavior:
- Defines `termchars` used by assignment parsing.
- `charin()` searches for delimiters while skipping single-quoted strings and `${...}` variable generators.
- `expandquote()` and `escapetoken()` implement rc single-quote handling.
- `copyq()` preserves quoted/backquoted fragments while printing shell recipes.
- `bufcpyq()` appends strings with rc quoting when needed.

Important dependencies: `mk.h`, Plan 9 rune APIs, `needsrcquote`.

Notable risks:
- Only rc single quotes are true escapes; double quotes/backslashes are mostly preserved.
- Parser correctness depends on matching rc quoting rules.
