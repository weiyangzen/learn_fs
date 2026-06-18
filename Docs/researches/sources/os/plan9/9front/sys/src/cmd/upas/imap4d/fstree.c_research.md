# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fstree.c

This file manages an AVL tree mapping upas/fs message directory IDs to IMAP daemon `Msg` objects.

Key behavior:
- `fstreecmp` compares messages by `Msg.id`.
- `fstreefind` looks up a message id in a `Box`’s `fstree`.
- `fstreeadd` inserts a new `Fstree` wrapper and asserts uniqueness.
- `fstreedelete` removes a message id and asserts that it exists.

Integration and risks:
- Used to find daemon message structures by upas/fs directory id.
- Strict assertions make tree consistency failures fatal.
