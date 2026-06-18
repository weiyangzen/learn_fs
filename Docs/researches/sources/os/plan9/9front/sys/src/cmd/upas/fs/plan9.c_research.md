# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/plan9.c

This file implements traditional Plan 9 flat mbox-file backend support.

Key behavior:
- Parses Unix `From ` separators, validates dates with `strtotm`, and reads messages from an mbox file.
- Supports incremental append reading when qid.path matches but qid.vers changes.
- Merges newly read messages with indexed/existing messages by digest, marks disappeared messages, and detects duplicates.
- `writembox` rewrites the mailbox through `<path>.tmp`, preserving mode when possible and omitting deleted messages.
- `plan9syncmbox` optionally locks, reads mailbox, purges deleted messages, rewrites if necessary, and unlocks.
- `plan9mbox` accepts existing mbox files or `.tmp` recovery files and initializes backend callbacks.

Integration and risks:
- Stores whole mbox messages in memory and marks `mallocd`.
- Uses lock refresh during long reads/writes.
- Parser comment notes a known bug for very long lines with `From ` at buffer boundaries.
