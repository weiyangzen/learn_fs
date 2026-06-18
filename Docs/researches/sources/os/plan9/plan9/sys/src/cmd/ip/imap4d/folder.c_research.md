# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/folder.c

Mailbox filesystem helper layer for `imap4d`. It caches current directory changes, wraps create/open/stat/remove operations relative to mailbox directories, manages the global mailbox lock file `L.mbox`, and refreshes the lock during long copies.

It also converts IMAP modified UTF-7 mailbox names, constructs `.imp` sidecar names, creates nested mailboxes, renames or copies mailboxes, preserves permissions/group where possible, handles INBOX/mbox naming, and removes or truncates source mailboxes after successful moves/copies.
