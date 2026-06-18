# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/cat_mail.c

## Purpose
Local mailbox delivery implementation for `upas/send`.

## Behavior
Unescapes the target mailbox path, optionally prints dry-run output, locks the mailbox, opens it append-locked or falls back to `.tmp`, writes the message in mbox format via `m_print`, appends a blank line, flushes, unlocks, and logs delivery.

## Dependencies
`syslock`, `sysopen`, `m_print`, `logdelivery`, `refuse`.

## Risks / Notes
Retries open fallback up to five times, but a lock failure immediately refuses delivery.
