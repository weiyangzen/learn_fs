# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/unused/syscall.c

This file is an older unused syscall implementation covering files, namespace, directories, and network dial helpers.

Key behavior:
- Implements alternate versions of descriptor handling, close/create/dup/open/read/write/seek/stat/wstat/remove/chdir/bind/mount/unmount.
- Adds directory helpers `sysdirstat`, `sysdirfstat`, `sysdirwstat`, `sysdirfwstat`, and `sysdirread`.
- Implements network helpers `sysdial`, `sysannounce`, `syslisten`, plus internal `call`, `identtrans`, and `nettrans`.

Important details:
- This file is under `kern/unused`, and active syscall logic lives in `sysfile.c` plus libc `dial.c`.
- It shows older Plan 9 namespace and `/net/cs` calling conventions retained for reference.
