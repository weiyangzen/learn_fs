# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/gone.fishing.sh

## Purpose
Unix vacation/autoreply-style shell script.

## Behavior
Reads a message from stdin, appends it to `$HOME/gone.mail` with `From ` escaping, extracts the return sender from the first `From ` line, records senders in `$HOME/gone.addrs`, and sends a one-time auto-reply using `mail`.

## Dependencies
POSIX shell, `sed`, `tee`, `grep`, `mail`.

## Risks / Notes
Sender extraction is simplistic and based only on Unix `From ` line format.
