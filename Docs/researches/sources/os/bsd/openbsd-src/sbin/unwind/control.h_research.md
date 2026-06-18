# File Research: sources/os/bsd/openbsd-src/sbin/unwind/control.h

Header for `unwind` control socket support.

Declares:
- `control_init(char *)`
- `control_listen(int fd)`
- `control_accept(int, short, void *)`
- `control_dispatch_imsg(int, short, void *)`
- `control_imsg_relay(struct imsg *)`

Role:
- Exposes the control socket lifecycle and relay functions to the rest of the `unwind` daemon.
