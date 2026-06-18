# sources/user-network-fs/nfs-ganesha/src/include/os/linux/sys_resource.h

## Purpose
This Linux OS abstraction exposes a named helper macro for retrieving the process open-file limit.

## Important APIs, Types, And Control Flow
It includes `<sys/resource.h>` and defines `get_open_file_limit(rlim)` as `getrlimit(RLIMIT_NOFILE, (rlim))`.

## State And Persistence
No persistent state is defined. At runtime the macro reads process resource-limit state from the kernel.

## Dependencies And Integration Points
Consumers use it where platform-specific code needs to size descriptor management or report FD usage without hardcoding `RLIMIT_NOFILE`.

## Risks And Test Signals
Risk is small but return-value handling matters. Tests should verify startup behavior when `getrlimit` fails, low file-limit configurations, and FD usage reporting under Linux.
