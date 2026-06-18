# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/mbox.c

## Purpose
Core mailbox/message model for `upas/fs`. It creates mounted mailbox objects, parses RFC822/MIME message structure, exposes message files through the mail filesystem hash namespace, tracks deletion/refcounts, decodes bodies, converts charsets, and emits plumber notifications.

## Main Interfaces
- `newmbox`, `freembox`, `syncmbox`: mailbox lifecycle and backend dispatch.
- `parseunix`, `parseheaders`, `parsebody`, `parse`, `parseattachments`: split raw mail into headers, body, MIME parts, and exported filesystem entries.
- `newmessage`, `delmessage`, `delmessages`: message allocation and recursive deletion.
- `msgincref/msgdecref`, `mboxincref/mboxdecref`: lifetime management under mailbox locks.
- `decode`, `convert`, `decquoted`, `xtoutf`: content-transfer and charset decoding.
- `mailplumb`: sends `mailfs` plumb events for new/deleted mail.

## Behavior
`boxinit` tries IMAP4, POP3, Plan B, Plan B virtual, and Plan 9 mbox initializers in order. `parseheaders` recognizes common RFC822 and MIME headers, builds Unix `From ` fallback headers for POP3/IMAP messages, normalizes text bodies by squeezing NULs, and creates per-message file nodes such as `body`, `raw`, `header`, etc. MIME multipart parsing uses boundary scanning; `message/rfc822` parts are recursively parsed and may promote child headers to the wrapper part.

## Dependencies
Uses Plan 9 `String`, `plumb`, `libsec` SHA/base64 helpers, `tcs` for non-Latin1 charset conversion, global mailfs hash helpers (`henter/hfree`), and backend initializers declared elsewhere.

## Risks / Notes
- MIME boundary parsing is string-based and assumes boundary markers at line starts.
- `xtoutf` forks `/bin/tcs`; charset conversion failure silently leaves original bytes.
- `parseheaders` temporarily writes NUL into headers while extracting Received dates.
- Message deletion syncs only after refs drop, so stale refs delay physical purge.
