# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/plan9.c

## Purpose
Plan 9 traditional mbox backend for `upas/fs`, reading and rewriting single-file mailboxes with `From ` separators.

## Main Interfaces
- `plan9mbox`: recognizes accessible local mailbox paths and installs `plan9syncmbox`.
- `plan9syncmbox`: locks, reads/interpolates new mail, purges deleted mail, and rewrites if needed.
- `_readmbox`: incremental mailbox read/merge using qid path/version and previous length.
- `_writembox`: rewrites non-deleted messages through `<mbox>.tmp`.
- `purgedeleted`: removes deleted, unreferenced messages.

## Behavior
Messages are read by scanning for `\nFrom ` boundaries, SHA1-digested, parsed through `mbox.c`, and deduplicated against existing message digests. If the mailbox qid path is unchanged, it seeks to the old length to append-read new messages; if old messages disappear, they are marked deleted and optionally plumbed. Physical deletion rewrites the mailbox atomically via a temp file rename.

## Dependencies
Relies on `syslock`, `sysrename`, `sysopen`, `parseunix`, `parse`, `mailplumb`, `logmsg`, and SHA1 from `libsec`.

## Risks / Notes
- Message boundary detection depends on unescaped `From ` lines.
- Incremental read assumes qid path/version/length semantics faithfully identify append-only changes.
- Rewrite removes and renames files, preserving only basic mode bits.
