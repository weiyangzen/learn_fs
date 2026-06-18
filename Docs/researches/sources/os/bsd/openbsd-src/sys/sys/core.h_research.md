# File Research: sources/os/bsd/openbsd-src/sys/sys/core.h

This header preserves the obsolete NetBSD-style core file format used by binutils support.

Key definitions:
- Magic values: `COREMAGIC`, `CORESEGMAGIC`.
- `CORE_GETMAGIC`, `CORE_GETMID`, `CORE_GETFLAG`, `CORE_SETMAGIC` for network-byte-order mid/magic/flag encoding.
- Core flags: `CORE_CPU`, `CORE_DATA`, `CORE_STACK`.
- Userland structs: `struct core` and `struct coreseg`.

Kernel declarations:
- `coredump_write`
- `coredump_unmap`

Behavior and integration:
- The userland structures are explicitly marked obsolete and retained for binutils `netbsd-core` format support, especially a.out m88k/luna88k boot block workflows.

Risk notes:
- The header depends on network byte-order helpers and `_MAXCOMLEN` being available from includers.
- The old format is compatibility-only; modern OpenBSD ELF core notes are defined elsewhere.
