# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/pptpd.c

PPTP server-side helper for one TCP control connection and associated GRE tunnel.

Key behavior:
- Parses PPTP control messages from stdin/stdout, validates magic/type, and handles start, stop, echo, outgoing-call, call-clear, disconnect, WAN info, and link info.
- Allocates per-call `Call` objects in a hash table with refcounting and locks.
- `callalloc()` allocates a remote PPP IP via `dhcpclient`, starts `/bin/ip/ppp -SC`, stores PPP pipe fd, and launches PPP read and GRE timeout workers.
- `greinit()` dials GRE based on TCP connection path and remote IP.
- `greread()` validates GRE headers, looks up call id, updates ACKs, writes in-order PPP payloads to the call PPP fd, drops duplicates/out-of-order packets, and sends ACKs when receive window advances.
- `pppread()` reads PPP payloads, wraps them in GRE headers with key/sequence/ack, and waits for window space with timeout.
- `timeoutthread()` kills idle control sessions.

Integration:
- Designed to be launched by a TCP listener with a Plan 9 network connection directory argument.
- Uses `/bin/ip/dhcpclient` to allocate client addresses and `/bin/ip/ppp` to run PPP.
- Logs to syslog facility `pptpd`.

Risks and notes:
- `scallreq()` and `scallcon()` are explicitly unimplemented.
- `secho()` writes result byte into `p[16]` rather than response `buf[16]`, likely a bug.
- GRE packet handling has optional artificial drop support via `-D`.
- Refcounting is manual; correct `callfree()` pairing is essential.
