# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sock_notsupp.c

## Purpose
Provides a default `sock_downcalls_t` vector for protocol operations that are unsupported.

## Main Behavior
- Defines stub functions for accept, bind, listen, connect, name lookup, socket options, send, send-uio, receive-uio, poll, shutdown, ioctl, and close.
- All stubs return `EOPNOTSUPP` except `sock_clr_flowctrl_notsupp()`, which is a no-op.
- Exports `sock_down_notsupp`, a populated downcall table using those stubs.

## Integration Points
- Used by socket modules or protocol glue that need a complete downcall vector while explicitly marking operations unavailable.
- Depends on the public sockfs/socket protocol interfaces in `sys/socket_proto.h`.

## Risks and Notes
- `sock_poll_notsupp()` returns `EOPNOTSUPP` in a `short`, matching the downcall shape but semantically representing an unsupported operation rather than poll events.
- The table is intentionally simple and does not maintain socket state.
