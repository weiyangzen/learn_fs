# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/lex.c

Line assembly and lexical support for `mk` parser.

Key functions:
- `assline()` reads logical mkfile lines, skipping empty lines/comments and eliding escaped newlines.
- Handles quotes, backslashes, double quotes, and backquoted shell command substitutions.
- `bquote()` executes backquoted commands via `execsh()` and inserts output into the current buffer.
- `nextrune()` reads runes and treats escaped newlines either as elided or blank.

Behavior notes:
- Comments consume through newline; if the last char before newline was backslash, escaped-newline behavior is propagated.
- Backquote supports rc-style `` `{ ... } `` and sh-style `` `...` `` forms.
- Errors call `Exit()` after reporting syntax context.
