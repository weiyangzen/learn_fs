# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/eventlib.h

Public-style ISC eventlib interface imported into libc with private symbol remapping.

Defines opaque ID/context/event wrapper structs and callback types for:
- Connections
- File descriptor readiness
- Streams
- Timers
- Wait events

Provides:
- Byte-mask macros.
- Event flags such as `EV_READ`, `EV_WRITE`, `EV_EXCEPT`.
- Remapped APIs for context lifecycle, event dispatch, connect/listen, FD selection, stream read/write, timers, waits, and defers.

Uses legacy `__P` prototype compatibility when needed.
