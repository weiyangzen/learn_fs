# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/control.h

This header declares the `slaacd` control-socket interface when not building `SMALL`.

Key declarations:
- `control_init(char *)`
- `control_listen(int)`
- `control_accept(int, short, void *)`
- `control_dispatch_imsg(int, short, void *)`
- `control_imsg_relay(struct imsg *)`

Integration:
- Used by `slaacd` frontend/main code to initialize the control socket and relay control replies.

Risk notes:
- The API is guarded by `#ifndef SMALL`, so source files using it must share the same build condition.
