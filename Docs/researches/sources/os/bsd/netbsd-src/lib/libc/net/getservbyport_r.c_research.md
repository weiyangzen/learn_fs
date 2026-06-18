# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport_r.c

Reentrant service lookup by network-order port and optional protocol. `getservbyport_r()` opens service state, calls `_servent_getbyport()`, and closes unless stay-open mode is active.

The CDB path converts the requested port with `be16toh()`, constructs a key containing zero name length, protocol length, encoded port, and protocol bytes, then validates the returned record before parsing it. The plain-file path iterates service records and compares `sp->s_port` directly against the caller’s port value, with an optional protocol string check.
