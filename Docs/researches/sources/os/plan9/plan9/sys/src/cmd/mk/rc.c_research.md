# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/rc.c

Shell-syntax support for `mk` when using Plan 9 `rc`.

Key globals:
- `termchars = "'= \t"` for assignment parsing.
- `shflags = "-I"` for non-interactive rc.
- `IWS = '\1'`.

Key functions:
- `charin()` finds separator characters while respecting single quotes and `${...}` variable generators.
- `expandquote()` expands rc single-quoted strings.
- `escapetoken()` reads quoted tokens during lexical parsing.
- `copyq()` copies quoted and backquoted strings for shell-printing.

Behavior notes:
- Single quotes escape by doubling.
- Backslash and double-quote are not real rc escapes here; they are preserved.
