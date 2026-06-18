# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/util.c

This file provides allocation, string, file-slurp, and hash helpers for the Mail client.

`emalloc`, `erealloc`, `estrdup`, `estrjoin`, and `esmprint` wrap allocation and fail with `sysfatal` on OOM. `fslurp()` reads an fd into a NUL-terminated buffer, growing by 1.5x. `rslurp()` opens and reads a file relative to either the mailbox root or a message path.

`strhash()` is a djb2-style byte hash used for message-id lookup.
