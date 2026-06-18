# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/message.c

Implements a passive word-wrapped message panel.

Key behavior:
- `pl_textmsg()` draws text folded to a rectangle width.
- `pl_foldsize()` computes wrapped size for a target width.
- Message panels draw inside a passive box and request size based on folded text.
- Ignores input.

Important dependencies: UTF helpers `pl_nextrune`, `pl_runewidth`, font/draw primitives.

Notable risks:
- Wraps only at spaces; very long words are forced onto a line.
- Message text pointer is borrowed, not duplicated.
