# File Research: sources/os/bsd/dragonflybsd/sys/sys/lockf.h

Kernel-only byte-range locking structures. `lockf_range` records lock type, flags, start/end offsets, owner process, and list linkage. `struct lockf` keeps active and blocked range queues plus initialization state.

Kernel APIs include `lf_advlock`, `lf_count_adjust`, and `maxposixlocksperuid`. This is the VFS advisory locking support embedded by filesystem inode/vnode implementations.
