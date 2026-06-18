# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/filter.c

## Purpose
Local filtering delivery helper that routes a message to different mailbox files based on regexps.

## Behavior
Reads a remote-style message, strips local system prefix from sender, tests sender and optionally header/body against regexp/replacement pairs, rewrites the destination file path via `regsub`, locks the normal mailbox, opens selected mailbox or `.tmp`, appends the message, and logs delivery.

## Dependencies
`m_read`, `m_print`, Plan 9 regexp, `syslock`, `sysopen`, `logdelivery`.

## Risks / Notes
The normal mailbox is always locked even when delivering to another file, by design comment.
