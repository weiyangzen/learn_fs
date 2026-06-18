# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/translate.c

Read fully: 43 lines, 804 bytes. SHA-256 prefix: `787bce785ad57fbe`.

This file implements address translation by piping a destination through an external command stored in `dp->repl1`. `translate()` starts the process, reads newline-terminated stdout as translated recipients, converts newlines to spaces, and turns the accumulated text into a destination list with `s_to_dest()`.

Lines beginning `_nosummary_` set the global `nosummary` flag and are not included in translated output. Stderr is drained, and nonzero process exit status sets `dp->pstat`, stores stderr text in `dp->repl2`, and returns no translated list.

Integration: invoked for `d_translate` destinations from the send rewrite/delivery pipeline. It uses upas process/stream wrappers and the shared `dest`/`message` structures from `send.h`.

Risk notes: process output directly drives destination expansion. Failed translators communicate diagnostic text through stderr, so callers must preserve `dp->repl2` for useful refusal messages.
