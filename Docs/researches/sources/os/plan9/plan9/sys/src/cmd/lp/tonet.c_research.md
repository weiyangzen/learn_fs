# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/tonet.c

Read fully: 59 lines, 913 bytes. SHA-256 prefix: `e9b889fb221ef1f7`.

This is a minimal utility that dials a Plan 9 network address and copies stdin to the connection. `pass()` loops with a 10-minute alarm around each read/write cycle. `alarmhandler()` catches alarm notes and reports `alarm`. `main()` validates a single `network!destination!service` argument, installs the alarm handler, dials with default network `"net"`, and copies.

Risk notes: one-way only; no response is read. Timeout handling reports but returns through Plan 9 note handling.
