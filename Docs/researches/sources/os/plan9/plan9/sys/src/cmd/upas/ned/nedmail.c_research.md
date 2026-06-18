# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ned/nedmail.c

## Purpose
Interactive terminal mail reader/editor built on `/mail/fs`.

## Main Interfaces
- `main`: starts `upas/fs` if needed, opens/selects mailbox, enters command loop.
- `dir2message`, `file2message`: build an in-memory tree from mailfs directories and `info` files.
- `parsecmd`, `parseaddr`, `parsesearch`: command/range/search parser.
- Command handlers: print, raw print, delete/undelete, sync, save, write attachment, reply, forward, pipe, shell, help, file-by-sender.
- `flushdeleted`: sends deletion requests to `/mail/fs/ctl`.

## Behavior
The client represents mailfs messages as nested `Message` nodes. It prints concise headers, MIME trees, raw or processed content, chooses displayable multipart alternatives, pipes HTML through `htmlfmt`, plumbs image/pdf-like attachments, and delegates replies/forwards to `/bin/upas/marshal`. Save/write commands append raw messages to mbox files or write body parts to files.

## Dependencies
`/mail/fs`, `/bin/upas/fs`, `/bin/upas/marshal`, Plan 9 plumber, regexp library, `String`, mailbox helper routines.

## Risks / Notes
- Command parsing is ed-like and compact but hand-written.
- MIME display heuristics include empirical length thresholds for bad multipart/alternative mail.
- Some command execution uses `/bin/rc -c` with user-entered text by design.
