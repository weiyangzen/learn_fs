# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/planb.c

## Purpose
Plan B/mail2fs mailbox backend for `upas/fs`, supporting directory mailboxes and virtual folders.

## Main Interfaces
- `planbmbox`: recognizes directory mailboxes containing `list`.
- `planbvmbox`: recognizes virtual folder files beginning with six digits and `/`.
- `mbsync`, `mbvsync`: sync normal and virtual Plan B mailboxes.
- `readpbmbox`, `readpbvmbox`: enumerate real directory mailboxes or virtual folder lists.
- `readpbmessage`: loads one Plan B message from `raw` and `text`.

## Behavior
A Plan B message is reconstructed from its `raw` first line and `text` body, with the message path appended to the body as a hint for attachment access. Normal directory mailboxes walk month directories and numeric message directories; virtual mailboxes parse message paths out of a listing file and map them under `/mail/box/$user/msgs`.

## Dependencies
Uses `readmessage`, `parseunix`, `parse`, `mailplumb`, `delmessage`, Plan 9 `Dir` operations, and mailbox fields from `dat.h`.

## Risks / Notes
- File comment documents a known limitation: raw attachment text is not reconstructed, so IMAP/other clients cannot access attachments through this backend.
- Deleted non-virtual messages are archived by renaming message directories to `s.<id>`.
- Virtual folder input is capped at 2 MiB and logs a “folder too big” warning.
