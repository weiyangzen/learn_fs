# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mbox.c

Manages IMAP mailbox state over Plan 9 `upas/fs`, including mailbox open/refresh, `.imp` metadata files, UID assignment, flags, expunge/delete, and mailbox-name safety.

Key behavior:
- `openBox` maps `INBOX` to `msgs` or `mbox`, opens the mailbox through `/mail/fs/ctl`, builds a `Box`, reads message directories, then opens or creates the `.imp` file.
- `checkBox` refreshes message state when the backing `upas/fs` directory qid/version/mtime changes and optionally returns a held `.imp` mailbox lock.
- `readBox` scans numeric message directories, preserves existing `Msg` nodes, marks missing messages expunged, allocates new messages, reads message `info`, and assigns IMAP sequence numbers.
- `.imp` files persist `uidvalidity`, `uidnext`, message digest, UID, and flags. `openImp`, `parseImp`, `closeImp`, `createImp`, `emptyImp`, `wrImpFlags`, and `impFlags` maintain this format.
- `boxFlags` assigns UIDs to new messages and counts `\Recent`.
- `deleteMsgs` sends batched `delete` commands to `/mail/fs/ctl` for messages flagged `\Deleted`.
- `expungeMsgs` emits `EXPUNGE` responses when requested, removes expunged `Msg` nodes, renumbers sequences, and marks `.imp` dirty.
- `okMbox` rejects unsafe/internal mailbox names, optionally allowing only names from `imap.ok`.

Integration points:
- Owns the mailbox/UID persistence contract used by fetch/search/store/list code.
- Depends on `msgInfo`, `freeMsg`, path helpers, Plan 9 `Dir`/`Qid`, and global `username`, `mboxDir`.
- Uses `/mail/fs/ctl` as the control plane for opening, closing, and deleting mail messages.

Risks and notes:
- Duplicate message digest handling is explicitly fragile; comments note concurrent IMAP servers may temporarily disagree on UID mapping.
- `.imp` locking is central. Calls that mutate flags or UIDs must hold the mailbox lock via `openImp`.
- `okMbox` can switch behavior entirely if `imap.ok` exists, making allowed mailbox names deployment-configurable.
