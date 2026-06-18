# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/dial.c

Non-Plan 9 compatibility implementation of Plan 9-style `dial` for `tcpostio`. It parses destinations like `tcp!host!service` or `udp!host!service`, resolves the host/service, creates a socket or reserved-port socket, connects with a 30-second alarm timeout, and returns the connected fd.

Integration points:
- Used by `tcpostio.c` through `extern int dial(char*, char*, char*, int*)`.
- Supports optional debug logging through global `dial_debug`.

Risks:
- Several early error returns leak `tdest`.
- `sin.sin_port = htons(sp==0 ? atoi(servname) : sp->s_port)` appears wrong for `getservbyname`, whose `s_port` is already network byte order.
- SO_KEEPALIVE path checks the option but calls `setsockopt` with the current false value, so it likely does not enable keepalive.
- Uses IPv4-only legacy resolver APIs and `alarm`, which is process-global.
