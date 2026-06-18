# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/utils.c

Provides common utility routines for `imap4d`: string predicates, file reading, temporary-file creation, lock-spinning opens, qid lookup, named integer mapping, and fatal allocation wrappers.

Key behavior:
- `strrev`, `isdotdot`, `issuffix`, `isprefix`, `ciisprefix` support parsing and mailbox validation.
- `readFile` reads an entire fd into `parseBin` allocation with trailing NUL.
- `imapTmp` creates a single ORCLOSE temporary file under `/mail/box/$user/mbox.tmp.imp`, retrying if locked.
- `openLocked` retries `cdOpen` while a file appears locked.
- `fqid` extracts a file `Qid`.
- `mapInt` case-insensitively maps names to values.
- `estrdup`, `emalloc`, `ezmalloc`, `erealloc` abort the IMAP session via `bye` on OOM and tag allocations.

Integration points:
- Shared across list, mailbox, parser, and message modules.
- Uses globals `username`, `parseBin`, and Plan 9 allocation/debug APIs.

Risks and notes:
- `readFile` uses `long length` from `Dir.length`; very large files would not be safe, but inputs are small metadata files.
- Temporary file naming assumes only one temp is needed at a time per user mailbox.
