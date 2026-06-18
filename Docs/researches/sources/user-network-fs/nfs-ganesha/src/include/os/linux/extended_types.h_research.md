# sources/user-network-fs/nfs-ganesha/src/include/os/linux/extended_types.h

## Purpose
This is the Linux-specific extended type include. It centralizes standard integer and system type availability for common headers that include `extended_types.h`.

## Important APIs, Types, And Control Flow
It includes `<sys/types.h>` and `<stdint.h>` and declares no additional types or functions. Control flow is limited to the include guard.

## State And Persistence
No runtime state or persistence is involved.

## Dependencies And Integration Points
It is selected by the cross-platform `extended_types.h` wrapper on Linux. It provides the base type vocabulary used by RPC, quota, and OS abstraction headers.

## Risks And Test Signals
Risk is low but build-critical: removing or changing this include can break type visibility for transitive consumers. Test signals are clean Linux builds under strict warning modes and compile checks for headers that rely on `uint64_t`, `uid_t`, `gid_t`, and related scalar types.
