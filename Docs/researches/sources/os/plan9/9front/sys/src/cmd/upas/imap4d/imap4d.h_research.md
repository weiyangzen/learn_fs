# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.h

Central header for `imap4d`. It defines mailbox/message state, IMAP parser node structures, flag/search/fetch/store enums, global variables, and imports `fns.h`.

Major data structures:
- `Box`: selected/open mailbox state, including mailbox name, `/mail/fs` handle, `.imp` path, writability, dirty flags, qids, mtimes, message counters, UID counters, linked messages, and `fstree`.
- `Msg`: message or MIME part node with parent/child links, upas/fs directory path, cached headers, IMAP flags, expunge state, UID/sequence/id, raw body size/line counts, info fields, and parsed addresses.
- `Header`: cached RFC822/MIME header buffer plus parsed MIME header fields.
- `Maddr` and `Mimehdr`: parsed address and MIME parameter lists.
- `Mblock`: lock wrapper for mail file operations.
- `Fetch`, `Store`, `Search`, `Msgset`, `Nlist`, `Slist`: per-command parse trees allocated from `parsebin`.
- `Uidplus`: UIDPLUS response chain for append/copy operations.

Important enums:
- IMAP message flags: `Fseen`, `Fanswered`, `Fflagged`, `Fdeleted`, `Fdraft`, `Frecent`.
- Upas/fs `info` fields: sender/recipient/date/subject/type/digest/message-id/size fields.
- Fetch operators: `Fenvelope`, `Fflags`, `Frfc822`, `Fbody`, `Fbodysect`, `Fbodypeek`, etc.
- Fetch body section parts: `FPall`, `FPhead`, `FPheadfields`, `FPmime`, `FPtext`.
- Store operators: `Stflags`, `Stflagssilent`.
- Search keys: full IMAP search key set used by parser and evaluator.
- Status items: `Smessages`, `Srecent`, `Suidnext`, `Suidvalidity`, `Sunseen`.

Filesystem relevance:
- Constants such as `Pathlen`, `Filelen`, and lock timing shape all mailbox/path handling.
- `Box` explicitly bridges IMAP metadata with `/mail/fs` mailbox qids and `.imp` state files.

Notable constraints:
- Header comments state mailbox/message structures are manually allocated and freed.
- Parser nodes are intentionally arena-allocated so a parse error can discard the whole command parse tree.
