# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/folder.c

This file implements appending mail into either traditional mbox files or Plan 9 mail directories.

Key behavior:
- Tracks up to five open `Folder` records with type, lock, output fd, `Biobuf`, and timestamp.
- `openfolder` creates a directory if the target does not exist; directories use mdir-style files, non-directories use mbox append.
- `mboxopen` locks with `syslock`, opens/creates appendable mbox, seeks to end.
- `mdiropen` creates a unique `<time>.<seq>.tmp` file in a directory and `closefolder` renames it to `<time>.<seq>`.
- `appendfolder` reads an optional Unix `From ` line, writes one if missing, normalizes CRLF, escapes leading `From ` body lines, and flushes.
- `foldername` and `ffoldername` map user/mailbox/recipient strings to safe mailbox paths while refusing special files.
- `fappendfile` copies raw file data to a new target file.

Integration and risks:
- Must stay synced with send-side and imap4d mailbox safety checks per comments.
- Locks are described as traditional and partially best-effort; mdir writes rely on exclusive temporary file creation.
