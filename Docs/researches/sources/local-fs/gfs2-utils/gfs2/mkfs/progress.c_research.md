# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.c

Small terminal progress display helper adapted from e2fsprogs.

Key functions:
- `gfs2_progress_init`: initializes spacing/backspace buffers, records max count and digit width, prints an optional message unless quiet.
- `gfs2_progress_update`: once per second, if stdout is a tty, prints `[value/max]` and backspaces over it.
- `gfs2_progress_close`: clears tty progress text and prints an optional final message.

Internal state:
- Static `spaces[44]`, `backspaces[44]`
- Static `last_update`, throttling updates to one per second.

Research notes:
- Quiet mode sets `skip_progress`; non-tty stdout also suppresses live progress updates.
- Used by `main_mkfs.c` while adding journals and building resource groups.
