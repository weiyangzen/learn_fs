# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/list.c

Implements IMAP `LIST`, `LSUB`, and subscription file operations.

Key responsibilities:
- Traverses user mailbox directories under `mboxdir`.
- Encodes/decodes filesystem mailbox names and IMAP modified UTF-7 display names.
- Matches IMAP wildcard patterns `*` and `%` against mailbox paths.
- Determines whether directory entries are selectable mailboxes, folders, or ignored files.
- Maintains `imap.subscribed`.

Important functions:
- `mopen()` and `mdirstat()` open/stat mailbox-relative paths with path traversal checks.
- `chkmbox()` classifies paths as mailbox files, mailbox directories, or nonselectable folders.
- `dirskip()` mirrors upas/fs mailbox-directory heuristics by recognizing message directories.
- `output()` emits IMAP list responses with `\Noselect`, `\Noinferiors`, and `\Marked`.
- `lmatch()` recursively matches live mailbox hierarchy.
- `listboxes()` handles normal `LIST`.
- `opensubscribed()`, `trim()`, `pmatch()`, and `lsubboxes()` handle subscription file matching.
- `subscribe()` appends or removes entries in `imap.subscribed`.

Filesystem relevance:
- Performs mailbox discovery directly from `mboxdir`, using encoded filesystem names via `encfs()`/`decfs()`.
- Uses mailbox mtimes and `.imp` mtimes to decide `\Marked`.
- Locks subscription updates with `mblock()`.

Notable risks and quirks:
- Comments explicitly say mailbox identification duplicates upas/fs logic and must stay in sync with `../fs/mdir.c`.
- `subscribe()` opens a truncating `tfd` but writes through `fd`, which is suspicious.
- Pattern matching mutates strings temporarily and is recursive; malformed paths are mostly rejected through `mokmbox()`/`okmbox()`.
