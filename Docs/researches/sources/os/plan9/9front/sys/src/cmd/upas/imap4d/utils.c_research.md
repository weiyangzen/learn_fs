# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/utils.c

General utility functions for IMAP daemon support.

Key responsibilities:
- String helpers: `strrev()`, `isdotdot()`, `issuffix()`, `isprefix()`.
- `readfile()` reads an fd into the current `parsebin`.
- `imaptmp()` creates a lock-protected temporary file in the user mailbox directory.
- `openlocked()` repeatedly opens/creates locked files, recognizing Plan 9 filesystem lock error strings.
- `fqid()` extracts qids.
- `mapint()` case-insensitively maps names to integers.
- Memory helpers `emalloc()`, `ezmalloc()`, `erealloc()` exit via `bye()` on OOM.
- `setname()` rewrites `/proc/<pid>/args` for process display.

Filesystem relevance:
- Provides lock-aware file open behavior for mailbox metadata.
- `imaptmp()` targets `/mail/box/<username>/mbox.tmp.imp`.
- `setname()` changes process args to selected mailbox names.

Notable quirks:
- `readfile()` uses `parsebin`, so callers must ensure that arena lifetime is suitable.
- Lock retry error matching is string-based across multiple filesystem implementations.
