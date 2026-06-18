# sources/user-network-fs/nfs-ganesha/src/include/os/linux/quota.h

## Purpose
This header maps the common Ganesha quota abstraction to Linux `quotactl`.

## Important APIs, Types, And Control Flow
It includes `<sys/quota.h>` and defines `QUOTACTL(cmd, path, id, addr)` as a direct call to `quotactl((cmd), path, id, addr)`.

## State And Persistence
No header state exists. `quotactl` reads or mutates kernel/filesystem quota state depending on command.

## Dependencies And Integration Points
It is selected by `include/os/quota.h` on Linux and used by rquota service code and FSAL quota paths.

## Risks And Test Signals
Quota command encoding and privilege requirements vary by filesystem. Test signals include `GETQUOTA`/`SETQUOTA` RPC coverage, disabled-quota errors, user/group/project quota variants if supported, and Linux builds against current libc quota headers.
