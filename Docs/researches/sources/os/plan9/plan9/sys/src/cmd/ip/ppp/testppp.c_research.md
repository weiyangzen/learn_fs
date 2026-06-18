# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/testppp.c

Small PPP test harness that creates two Plan 9 IP stacks, launches two `ppp` instances, and shuttles bytes between them through pipes.

Key behavior:
- Parses test flags for compression, IP compression, PPP framing, MTU, debug level, packet error rate, packet drop rate, and alternate PPP executable.
- `pppopen()` forks and execs the PPP daemon with one side bound to `/net.alt2` and the other to `/net.alt`.
- `xfer()` forks transfer loops in both directions, optionally corrupting bytes or dropping packets using `lnrand()`.
- Debug mode prints short packet previews with printable characters and hex bytes.

Integration:
- Exercises `/bin/ip/ppp` or a provided PPP binary via standard input/output.
- Uses Plan 9 `bind("#I*", ...)` to create alternate network mounts.

Risks and notes:
- Intended as a destructive/fault-injection test tool, not production code.
- `pppopen()` exits with `exits(0)` on fork failure, which hides failure status.
