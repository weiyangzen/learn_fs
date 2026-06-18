# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/copy.c

Message copy and append storage support for `imap4d`. It verifies source messages, reads unix headers and raw bodies from upas/fs, spools APPEND literals through a temporary file while normalizing CRLF and escaping `From ` lines, then appends to the target mailbox.

`saveMsg` holds the mailbox lock, appends message data, computes SHA1 digests for newly appended messages, refreshes the lock during long writes, and updates the `.imp` sidecar with digest, UID placeholder, and flags.
