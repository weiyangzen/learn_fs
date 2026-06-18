# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/sys_resource.h

## Purpose
This FreeBSD resource-limit shim provides the common `get_open_file_limit()` name used by portable Ganesha code.

## Important APIs, Types, And Functions
It includes `<sys/resource.h>` and defines `get_open_file_limit(rlim)` as `getrlimit(RLIMIT_NOFILE, (rlim))`.

## Control Flow
Callers invoke the common wrapper-like macro with a `struct rlimit *`; the macro directly evaluates to the system `getrlimit` call for open-file limits.

## State And Persistence
No state is stored. The macro reads process resource-limit state and writes into caller-provided memory.

## Dependencies And Integration Points
It integrates generic resource-limit initialization code with FreeBSD's standard `getrlimit` API and mirrors the Darwin header's declared wrapper name.

## Risks And Test Signals
Risks include macro side effects if the argument expression has side effects and lack of function-address compatibility compared with platforms that declare a real function. Test signals include FreeBSD compile tests, runtime comparison with direct `getrlimit(RLIMIT_NOFILE, ...)`, and call sites that do not attempt to take the wrapper's address.
