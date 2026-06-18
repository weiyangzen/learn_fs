# File Research: sources/os/bsd/dragonflybsd/sys/sys/devicestat.h

Device I/O statistics ABI and kernel accounting interface.

Key responsibilities:
- Defines `DEVSTAT_VERSION` and warns it must change when struct/enumeration ABI changes.
- Defines support flags, transaction direction flags, tag types, device priority classes, and device/interface type flags.
- Defines `struct devstat` with queue linkage, device identity, byte and operation counters for reads/writes/frees/other, busy count, block size, tag counters, creation/busy/start/completion times, support flags, device type, and priority.
- Declares kernel functions to add/remove entries and start/end transactions, including buffer-based completion.

Dependencies:
- Includes queue, time, and types headers.

Notable risks:
- Userland statistics consumers rely on exact struct/enumeration layout and `DEVSTAT_VERSION`.
- Busy-time accounting depends on balanced start/end transaction calls.
