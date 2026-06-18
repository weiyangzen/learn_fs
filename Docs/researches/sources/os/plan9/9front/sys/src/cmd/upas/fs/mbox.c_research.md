# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/mbox.c

This file is the core mailbox/message manager and MIME parser for `upas/fs`.

Key behavior:
- `syncmbox` loads index state, calls backend sync, caches/plumbs new or modified messages, deletes removed messages, writes stale index state, and bumps mailbox versions.
- `newmbox` selects backend initializers in order: IMAP, POP3, mdir, Plan 9 mbox.
- Manages mailbox close/remove/rename, references, message allocation/freeing, and message tree deletion.
- Parses headers, dates, addresses, references, content type, transfer encoding, disposition, filename, charset, multipart boundaries, nested RFC822 messages, and MIME parts.
- Decodes base64 and quoted-printable bodies, converts charsets to UTF-8 via direct Latin-1 conversion or `/bin/tcs`.
- Sends plumb notifications for new/modified/deleted mail and optional biff output.
- Provides control helpers for deleting, flagging, and moving messages.

Integration and risks:
- Central user of `cache.c`, `idx.c`, `header.c`, `mtree.c`, and all mailbox backends.
- Address/header parsing is pragmatic rather than fully RFC-complete.
- `eprint` and `iprint` reuse a `va_list` twice after `vseprint`, which is undefined in standard C; Plan 9 compiler/runtime may tolerate this, but it is fragile.
