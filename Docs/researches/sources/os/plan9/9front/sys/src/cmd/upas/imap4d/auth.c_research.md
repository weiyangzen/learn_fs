# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/auth.c

This file implements authentication and post-login setup for the IMAP4 daemon.

Key behavior:
- `enableforwarding` temporarily marks the remote peer as trusted in `/mail/ratify` for SMTP forwarding.
- `setupuser` switches/chowns to authenticated user, creates a namespace, optionally binds alternate upas binaries, changes to mailbox dir, and starts `upas/fs -np`.
- Supports CRAM-MD5 (`cramauth`), Plan 9 challenge-response (`crauth`), password-to-CRAM verification (`passauth`), and SASL PLAIN (`plainauth`).
- Handles base64 client responses and cancellation with `*`.

Integration and risks:
- Relies on globals from `imap4d.h` such as `bin`, `bout`, `username`, `remote`, `mboxdir`, `binupas`.
- Contains a hard-coded debug branch checking `argv0` for `8.out` and launching `/sys/src/cmd/upas/fs/8.out`; this is unusual production behavior.
