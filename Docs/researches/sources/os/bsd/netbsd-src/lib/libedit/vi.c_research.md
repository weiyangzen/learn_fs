# File Research: sources/os/bsd/netbsd-src/lib/libedit/vi.c

## Purpose
Implements libedit's vi editing commands and vi command-mode behavior.

## Main Components
- `cv_action()` handles vi operator prefixes such as delete/change/yank, including repeated operator forms like `dd`, `cc`, and `yy`.
- `cv_paste()` implements paste before/after cursor using the kill buffer.
- Movement commands cover previous/next word, big-word variants, end-word variants, column movement, character search, repeated search, history search, matching bracket navigation, and history-line jumps.
- Editing commands cover case change, insert/append, replace modes, substitute char/line, change-to-EOL, delete previous char, kill-to-BOL, yank, comment current command, and redo/undo.
- Mode commands switch between insert and vi-command maps and manage pending arguments/actions.
- `vi_histedit()` writes the current or selected history line to a temporary file, invokes `$EDITOR` or `vi`, reads the result, and submits it.
- Alias and history-word commands integrate shell-like vi behavior into libedit.

## Integration
Uses common character-edit helpers, emacs helpers where behavior overlaps, history helpers, terminal output, wide-character conversion, and libedit key maps.

## Risks / Notes
- Many commands depend on shared `el_chared` state for undo, redo, kill buffer, and pending vi action.
- `vi_histedit()` uses `/tmp/histedit.XXXXXXXXXX`, fork/exec, and multibyte conversion; failures return `CC_ERROR`.
- Cursor boundary behavior is carefully adjusted for vi semantics and may differ from POSIX or historical NetBSD vi in noted cases.
