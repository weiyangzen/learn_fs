# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs.h

This header defines procfs node types and the in-memory `pfsnode`. `pfstype` enumerates root, curproc symlink, process directory, executable symlink, memory, registers, FP registers, debug registers, control, status, note, process-group note, map, executable type, cmdline, and resource limits.

`struct pfsnode` stores hash linkage, associated vnode, node type, pid, mode bits, open flags, unique file number, and a per-node lock.

The header defines helper macros for component-name matching, synthetic file-number generation, vnode/pfsnode conversion, and the `CHECKIO` authorization predicate for debugging-sensitive operations.

It declares procfs allocation/free, process lookup/release helpers, per-file handlers, register access functions, validity predicates, root lookup, and generic read/write dispatch.

Research notes: `CHECKIO` is central to security. It permits same-real-user debugging when setuid/exec restrictions are absent, or privileged override via capability checks.
