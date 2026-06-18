# File Research: sources/os/plan9/9front/sys/src/cmd/mk/lex.c

Assembles logical mkfile lines and evaluates backquoted commands during lexical input.

Key behavior:
- `assline()` skips blank lines/comments, strips carriage returns, handles escaped newlines, quoted strings, and backquotes.
- `bquote()` supports rc-style `` `{...}` `` and sh-style backquotes, runs the command with `execsh`, and replaces the source text with command output.
- `nextrune()` centralizes escaped-newline handling and line counting.

Important dependencies: `mk.h`, `Biobuf`, `escapetoken`, `execsh`, `execinit`.

Notable risks:
- Backquote evaluation happens during parsing and can execute arbitrary commands from mkfiles.
- Missing quote/backquote errors terminate mk.
