# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mbox.c

Implements mailbox open/check/close, message discovery, `.imp` synchronization, expunge, create/rename/remove operations, and mailbox name validation.

Key responsibilities:
- Talks to `/mail/fs/ctl` to open, create, rename, remove, close, and delete messages.
- Builds `Box` state from `/mail/fs/<handle>` directories.
- Detects new/deleted messages and marks pending expunges.
- Opens/creates/parses/writes `.imp` state under mailbox lock.
- Assigns UIDs and sequence numbers.
- Deletes messages marked `\Deleted`, then removes expunged `Msg` objects.

Important functions:
- `fsinit()` opens `/mail/fs/ctl`.
- `openbox()` opens a mailbox in upas/fs, reads message directories, opens `.imp`, sequences messages, and returns a `Box`.
- `readbox()` scans upas/fs message directories, creates `Msg` records, calls `msginfo()`, and updates `fstree`.
- `openimp()` locks and synchronizes `.imp` state, creating it when absent.
- `checkbox()` refreshes a box based on qid/mtime changes and optionally keeps the `.imp` lock open.
- `closeimp()` writes dirty `.imp` state.
- `closebox()` optionally deletes and expunges messages, closes the upas/fs handle, and frees all state.
- `deletemsg()` batches `/mail/fs/ctl` delete commands.
- `expungemsgs()` emits IMAP `EXPUNGE` and unlinks freed messages.
- `okmbox()` rejects reserved or dangerous mailbox names.
- `creatembox()`, `renamebox()`, `removembox()` call upas/fs control operations.

Filesystem relevance:
- This is the core filesystem bridge for IMAP. It models `/mail/fs` message directories and sidecar `.imp` files.
- Locks mailbox metadata with `mblock()` and uses qids/mtimes as change detectors.
- Maintains an AVL tree from upas/fs numeric message id to `Msg`.

Notable risks and quirks:
- Comments document the `.imp` file format and its locking assumptions.
- `readbox()` uses a `Gone` bit overlay in `expunged` to track unseen messages during refresh.
- `sequence()` sorts by UID, not filesystem order, and aborts if existing sequence numbers conflict.
- `renamebox()` notes the lock may be needed and relies on upas/fs moving `.imp`.
