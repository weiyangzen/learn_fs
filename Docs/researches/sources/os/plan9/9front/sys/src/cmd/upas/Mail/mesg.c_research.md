# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mesg.c

This file loads, opens, displays, and manages individual messages. `mesgload()` reads a message `info` file from `/mail/fs`, parses ordered metadata fields, derives flags, date/time, digest, message-id hash, and a display `fromcolon`.

Multipart handling is lazy. `readparts()` recursively scans attachment directories, records parts, and selects a preferred body, favoring `text/plain` then `text/html`. `mesgopenbody()` opens the chosen body directly or pipes HTML through `/bin/htmlfmt -cutf-8`.

`mesgshow()` writes message headers, thread links, body text, and attachment helper commands into an Acme window. Event handling supports `Reply`, `Reply all`, `Delmesg`, `Del`, and `Mark`. Opening a message marks it seen in `/mail/fs` and redraws the mailbox line.
