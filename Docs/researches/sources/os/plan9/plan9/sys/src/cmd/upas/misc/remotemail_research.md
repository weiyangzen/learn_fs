# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/remotemail

## Purpose
Remote SMTP delivery wrapper used by the mail queue.

## Behavior
Shifts queue/control arguments to isolate sender and destination address, then runs `/bin/upas/smtp -g research.research.bell-labs.com $addr $sender $*`.

## Dependencies
Plan 9 `rc`, `/bin/upas/smtp`.

## Risks / Notes
Gateway host is hard-coded.
