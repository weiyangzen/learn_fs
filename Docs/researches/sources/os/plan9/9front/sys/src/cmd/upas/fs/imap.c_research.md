# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/imap.c

This file implements the IMAP4 client backend for `upas/fs`.

Key behavior:
- Supports `/imap/host[/user[/mailbox]]` and `/imaps/...` mailbox paths.
- Handles IMAP quoting (`%Z`), UID formatting (`%U`), tagged commands, response parsing, capabilities, status, fetch, expunge, and flags.
- Supports CRAM-MD5, NTLM, and password login via Plan 9 auth/factotum.
- Maintains `Fetchi` arrays of UID/size/date/flags state, detects new/deleted/modified messages, and maps server UIDs into message state.
- Fetches message body ranges with `uid fetch ... body.peek[]<offset.length>`, including a Gmail size workaround.
- Implements remote delete, move via `UID COPY` plus `\Deleted`/`EXPUNGE`, flag updates, mailbox rename, refresh/debug controls, and TLS-wrapped SSL connections.

Integration and risks:
- Provides `Mailbox.fetch/delete/move/sync/ctl/rename/modflags` callbacks.
- Uses `idxaux` to persist IMAP UID identity across index reloads.
- Parser is lowercase/mutating and intentionally compact; malformed or unexpected server responses often return `confused` and may abort a sync.
- No STARTTLS path here; SSL is via `/imaps/` and `wraptls`.
