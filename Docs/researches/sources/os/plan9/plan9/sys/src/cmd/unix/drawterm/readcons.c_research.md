# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/readcons.c

Implements console prompting and small allocation helpers for drawterm.

Functions:
- `erealloc` and `estrdup` abort with `sysfatal` on allocation failure.
- `estrappend` appends formatted text to a dynamically allocated string.
- `readcons(prompt, def, raw)` prompts on `/dev/cons`, optionally enables raw mode via `/dev/consctl`, reads one byte at a time, handles newline, delete, backspace, and `^U`, and returns the entered string or default.

Notable behavior:
- Raw mode is used for password-like input; it writes a newline and turns raw mode off when input completes.
- Delete (`0x7f`) cancels and returns nil.
