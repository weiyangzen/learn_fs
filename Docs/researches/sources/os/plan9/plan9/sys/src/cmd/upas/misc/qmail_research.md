# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/qmail

## Purpose
Queue-and-run helper for remote mail.

## Behavior
Takes sender/address arguments, invokes `qer /mail/queue mail ...` to enqueue the message, then runs `runq /mail/queue /mail/lib/remotemail` if queueing succeeds.

## Dependencies
Plan 9 `rc`, `qer`, `runq`, `/mail/lib/remotemail`.

## Risks / Notes
No argument validation beyond positional shell assignments.
