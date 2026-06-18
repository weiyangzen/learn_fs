# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_pton.c

Implements standard `inet_pton`.

Behavior:
- Dispatches by address family; unsupported families set `EAFNOSUPPORT`.
- IPv4 parser has a `pton` flag: strict `inet_pton` mode requires decimal dotted-quad only, though the helper can also support legacy hex/octal/shorthand for other callers.
- IPv6 parser handles hex words, `::`, and embedded IPv4 dotted-quad.
- On invalid presentation format returns `0` without touching destination; on unsupported family returns `-1`.

Uses ISC-derived parser logic and asserts non-null input/output.
