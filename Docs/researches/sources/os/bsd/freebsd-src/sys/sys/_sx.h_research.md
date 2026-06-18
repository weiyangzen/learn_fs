# File Research: sources/os/bsd/freebsd-src/sys/sys/_sx.h

Shared/exclusive lock structure definition.

Key elements:
- Defines `struct sx` with common `lock_object` and volatile `sx_lock`.

Dependencies:
- Includes `sys/_types.h` and `sys/_lock.h`.

Research notes:
- SX locks are sleepable shared/exclusive kernel locks.
- Used by VFS and filesystem code where blocking while locked is acceptable.
