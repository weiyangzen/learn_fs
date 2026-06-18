# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/lex.c

Lexer for rc syntax.

Main features:
- Character classification through `wordchr()` and `idchr()`.
- One-character lookahead with `nextc()`/`advance()`.
- `getnext()` reads command input, handles line continuations, prompting, echo flags, EOF, and comments.
- `pprompt()`, `skipwhite()`, `skipnl()`, `nextis()` support parser interaction.
- Token construction uses `tok` with UTF-preserving `addutf()`.
- `yylex()` recognizes:
  - variable operators `$`, `$#`, `$"`;
  - `&&`, `||`;
  - pipes and redirections including fd forms;
  - quoted strings with doubled quote escaping;
  - implicit concatenation `^` after words;
  - subscript `(` after words;
  - glob metacharacter marking;
  - keywords via `klook()`.

Risk/notes:
- Parser context flags `lastdol` and `lastword` alter tokenization.
- Redirection token trees are allocated directly in the lexer.
- Comments are skipped regardless of quote state per the current comment in code.
