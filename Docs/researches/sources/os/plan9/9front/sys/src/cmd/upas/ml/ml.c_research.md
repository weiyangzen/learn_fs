# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/ml.c

Main remailer for a simple mailing list.

Key responsibilities:
- Reads a queued/delivered message from stdin, discarding the Unix `From ` line.
- Parses RFC822 headers to identify sender.
- Reads subscriber address-list file.
- Optionally enforces private-list membership.
- Rewrites headers: removes `Reply-To` and `Precedence`, prefixes subject with `[listname]`, adds list `Reply-To`, and sets `Precedence: bulk`.
- Starts a mailer to all list members.
- Archives the message to the list mailbox if the archive exists.

Important functions:
- `printsubject()` preserves existing subject while avoiding duplicate list prefix.
- `printmsg()` streams original message with selected headers filtered/replaced.
- `appendtoarchive()` appends to `listname/mbox` if present.
- `main()` coordinates parsing, membership check, sending, waiting, and archiving.

Filesystem relevance:
- Reads address-list file.
- Appends to list archive mailbox through folder helpers if it exists.
- Uses upas mailbox conventions for list-owned mailboxes.

Notable quirks:
- Reads up to 2 MiB of message content.
- Prevents remailing messages apparently from the list itself.
