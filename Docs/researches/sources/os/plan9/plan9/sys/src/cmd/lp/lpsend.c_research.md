# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/lpsend.c

Read fully: 318 lines, 6064 bytes. SHA-256 prefix: `25f16e415b7663e2`.

This command sends a print job to a network lp daemon using a simple two-step protocol: read an options line from stdin, spool the remaining stdin to a temporary file to know its size, dial the destination, send options, send size, wait for ACK, send data, send ACK, wait for final ACK, then relay daemon response to stdout.

It contains compatibility branches for Plan 9 and non-Plan 9 systems. Helpers include `readline()`, `pass()`, `prereadfile()`, `tempfile()`, `recvACK()`, and alarm/error handling.

Integration: pairs naturally with `lpdaemon.c`’s non-BSD/simple protocol path.

Risk notes: temp file names are predictable (`/tmp/lp<pid>.<idx>` on non-Plan 9). Uses alarms to prevent network hangs.
