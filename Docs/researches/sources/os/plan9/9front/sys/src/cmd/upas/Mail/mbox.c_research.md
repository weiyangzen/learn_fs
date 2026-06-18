# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mbox.c

This is the main mailbox controller for Acme `Mail`. It loads `/mail/fs/<mailbox>`, builds `Mesg` objects, sorts by time, groups messages into threads using `Message-ID`/`In-Reply-To`, tracks dummy placeholders, and keeps a message-id hash table.

It handles plumber channels for new/modified/deleted mail, show-mail requests, and send-mail requests. It also reads Acme mailbox events and dispatches commands: `Put`, `Mail`, `Delmesg`, `Undelmesg`, `Del`, `Redraw`, `Next`, `Mark`, and `Filter`.

Rendering is controlled by `listfmt`, with directives for subject, from, to, cc, reply-to, indentation, child markers, and date formatting. `mbflush()` applies pending deletions to `/mail/fs/ctl`, removes zapped messages, reparents thread children, and updates the Acme buffer. Quit logic protects open message/compose windows and dirty mailbox buffers.
