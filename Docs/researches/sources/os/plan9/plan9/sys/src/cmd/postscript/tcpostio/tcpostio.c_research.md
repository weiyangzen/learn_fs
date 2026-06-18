# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/tcpostio.c

Purpose: Sends PostScript or printer data to a network printer while concurrently reading printer status.

Key behavior:
- Implements a two-process protocol over a Unix `socketpair`.
- Parent `readprinter` polls printer status with control-T requests and parses `%[ status: ... ]%` messages.
- Child `sendfile` waits for `SEND_DATA` commands, writes chunks to the printer, sends EOT, and waits for end-of-job acknowledgement.
- `parsmesg` normalizes printer status strings into internal states: initializing, idle, busy, waiting, printing, printererror, Error, flushing, unknown.
- `getline` reads until newline, EOT, timeout, or buffer limit.
- Options configure block size from baud rate and debug verbosity.

Dependencies and integration:
- Uses `dial` from `dial.c`.
- Assumes printers understand control-T status requests and EOT framing.
- Intended as a printer transport companion for PostScript output tools.

Risks and notes:
- Protocol is timing-sensitive and uses alarms, sleeps, and select timeouts.
- `fprintf(stderr, buf)` prints printer-provided text as a format string, which is unsafe in modern terms.
- `blocksize = baud/10` is a throughput heuristic.
- Parent/child exit status is ORed; behavior depends on Plan 9/Unix wait status representation.
