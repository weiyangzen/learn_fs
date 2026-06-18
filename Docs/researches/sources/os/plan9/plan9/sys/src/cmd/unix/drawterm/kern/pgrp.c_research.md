# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/pgrp.c

This file implements hosted drawterm process-resource groups: process groups, rendezvous groups, file-descriptor groups, and mount records.

Key behavior:
- `newpgrp`, `closepgrp`, `pgrpcpy`, `pgrpinsert` manage namespace/mount group allocation, ordered mount insertion, and cloning.
- `newrgrp`, `closergrp` allocate and release rendezvous groups.
- `dupfgrp`, `closefgrp` duplicate and close file descriptor tables with channel refcount handling.
- `newmount`, `mountfree` allocate mount objects and release mounted channels/spec strings.
- `pgrpnote` is compiled out under `NOTDEF`; `resrcwait` prints exhaustion diagnostics.

Important details:
- `pgrpcpy` deep-copies mount headers and mount lists while incrementing mounted channel refs.
- `dupfgrp` copies only live descriptors and increments channel refs, preserving `maxfd`.
- File-descriptor table growth and syscall wrappers are in `sysfile.c`; this file owns the group lifetime pieces.
