# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/fs.c

This is the main `upas/fs` 9P file server. It exposes mailboxes and messages as a mounted file tree under `/mail/fs` or a supplied mount point.

Key behavior:
- Defines `Fid` state for active 9P fids, current qid, mailbox/message refs, open state, and directory-read finger optimization.
- `main` parses server flags, creates/mounts/posts the service, opens the default mailbox unless disabled, and forks the 9P server process.
- Implements 9P handlers for version/auth/attach/walk/open/create/read/write/clunk/remove/stat/wstat.
- Exposes top-level `ctl`, mailbox directories, message directories, and message pseudo-files such as `body`, `raw`, `rawbody`, `header`, `info`, flags, addresses, MIME fields, digest, and sizes.
- `rwrite` handles control commands: open/create/close mailbox, delete/flag/move messages, remove and rename mailboxes.
- Maintains a name/qid hash table for efficient walk lookup and a special `"xxx"` entry for message subfile lookup.
- `reader` periodically syncs mailboxes for plumbing/biff notifications.
- `readheader` filters ignored headers from `/mail/lib/ignore` and RFC2047-decodes output.

Integration and risks:
- Central coordinator for `dat.h`, cache/indexing, local/remote mailbox backends, MIME parsing, and Plan 9 9P.
- Uses global `synclock` to serialize 9P request handling and sync activity.
- `sanembmsg` contains a reference to `end` in a condition (`m->start > end`) that appears suspicious unless supplied by macro/environment; this code path should be treated carefully.
- Many reads force cache population and can trigger network fetches for IMAP/POP-backed mailboxes.
