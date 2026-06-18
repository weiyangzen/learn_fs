# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysid.h

Defines DragonFly system resource identifiers.

Key contents:
- Defines `sysid_t` as `u_int64_t`.
- Documents two SYSID classes:
  - physical SYSIDs for routing across a mesh
  - logical SYSIDs for persistent resources such as devices, media, or filesystems

Important concepts:
- Physical SYSIDs can change and can be recalculated.
- Logical SYSIDs can persist in superblocks or other metadata and support migration/multihoming.
- Logical plus physical SYSID validates message targets and drives route refresh.

Research notes:
- This is a small but foundational distributed-resource identity header.
- It is consumed by `sysref.h` for resource registration and lookup.
