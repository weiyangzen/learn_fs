# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/xec.c

Executes parsed `sam` commands.

Key functions:
- `cmdexec` resolves default addresses, loads unread files, selects the current file, and dispatches through `cmdtab`.
- Command handlers implement append/change/delete, file open/read/edit/write, global/ inverse-global, insert, mark, move/copy, print, quit, substitute, undo/redo, shell commands, file loops, line loops, and address display.
- `append` inserts command text and updates `ndot`.
- `display` emits selected text to terminal or stdout.
- `looper`, `linelooper`, and `filelooper` implement `x/y`, line iteration, and `X/Y` file iteration.

Behavior notes:
- `s_cmd` supports `&` and `\1`-style replacement expansion from regex submatches.
- `g_cmd` uses `execute(...) ^ cp->cmdc=='v'` to implement both `g` and `v`.
- Nested command execution is tracked with `nest`; file-loop nesting is guarded by `Glooping`.

Risk/maintenance notes:
- Editing operations depend on shared globals `addr`, `sel`, `genstr`, and `seq`.
- Substitution explicitly avoids infinite loops on empty matches by tracking the previous match endpoint.
