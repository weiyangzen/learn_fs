# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/receive.c

Command-line entry point for receiving a fax from stdin/stdout-connected modem service.

Key behavior:
- Parses `-v` for logging and `-s dir` for spool directory.
- Initializes a single `Modem` on fd 0 with no control fd.
- Calls `faxreceive()`.
- On successful receive, logs the result and execs `receiverc` with document id, success flag, page count, and optional FTSI.

Important implementation details:
- Default spool is `/mail/faxqueue`.
- Default post-receive script is `/sys/lib/fax/receiverc`.
- `receivedone()` does not run the script on receive failure.

Risks and invariants:
- If `exec(receiverc, argv)` fails after a successful receive, the process exits with `can't exec`.
