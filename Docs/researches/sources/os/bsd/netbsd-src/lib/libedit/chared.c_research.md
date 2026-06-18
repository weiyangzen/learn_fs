# File Research: sources/os/bsd/netbsd-src/lib/libedit/chared.c

This file implements libedit's low-level character editing utilities. It owns line-buffer mutation, vi undo/redo/yank bookkeeping, kill buffer handling, word movement helpers, buffer growth, and public insert/delete/replace cursor APIs.

Key state:
- `el->el_line` holds the editable wide-character line buffer, cursor, last character, and limit.
- `el_chared.c_undo` stores vi undo snapshots.
- `el_chared.c_redo` stores vi redo command metadata and buffer.
- `el_chared.c_kill` stores yanked/killed text and mark.
- `el_chared.c_vcmd` stores an active vi operator action and start position.

Key functions:
- `cv_undo()` snapshots the current line and redo metadata.
- `cv_yank()` copies a text range into the kill buffer.
- `c_insert()`, `c_delafter()`, `c_delafter1()`, `c_delbefore()`, and `c_delbefore1()` perform primitive buffer edits.
- `ce__isword()`, `cv__isword()`, and `cv__isWord()` classify word characters for emacs/vi movement.
- `c__prev_word()`, `c__next_word()`, `cv_next_word()`, `cv_prev_word()`, and `cv__endword()` implement word navigation.
- `cv_delfini()` finalizes a vi delete/yank/change operator.
- `ch_init()`, `ch_reset()`, `ch_enlargebufs()`, and `ch_end()` manage editor buffers.
- `el_winsertstr()`, `el_deletestr()`, `el_deletestr1()`, `el_wreplacestr()`, and `el_cursor()` are public editing helpers.
- `c_gets()` reads a small prompt response for extended commands.
- `c_hpos()` computes cursor horizontal position in a multiline buffer.
- `ch_resizefun()` and `ch_aliasfun()` store application callbacks.

Important control flow:
- Buffer expansion reallocates line, kill, undo, redo, and history buffers together, preserving pointer offsets.
- Vi delete/change operations use `c_vcmd.action` flags (`DELETE`, `INSERT`, `YANK`) and call `cv_delfini()` after motion commands.
- Deletion primitives update undo/yank state for non-emacs maps.

Risks and notes:
- `ch_init()` has multiple allocation steps; on failure it delegates to `ch_end()` for cleanup.
- Many operations assume internal buffers were initialized and sized consistently.
- `el_deletestr1()` bounds checks are conservative and does not delete if `end >= line_length`, so callers must understand its exact range semantics.
