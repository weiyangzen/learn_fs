# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/copy.c

This file implements IMAP COPY and APPEND save paths into local mailboxes.

Key behavior:
- `copycheck` verifies source messages are not expunged and have `rawunix` content.
- `opendeliver` forks `/bin/upas/mbappend` and returns a pipe to feed message data.
- `savemsg` streams a message into `mbappend`, computes SHA1 digest, then appends flags/UIDPLUS metadata to the target `.imp`.
- `copysave` and `copysaveu` copy existing message files and collect UIDPLUS results.
- `spool` reads APPEND literal data, normalizes CRLF to LF into a temporary file, and returns mapped size.
- `appendsave` prompts for literal data, spools it, then saves through `savemsg`.

Integration and risks:
- Uses mailbox lock (`mblock`) around `.imp` update, not around `mbappend`.
- Comments note this exists mainly to preserve flags and should ideally use upas/fs flags instead.
