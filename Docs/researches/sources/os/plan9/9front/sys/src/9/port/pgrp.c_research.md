# File Research: sources/os/plan9/9front/sys/src/9/port/pgrp.c

Process group, rendezvous group, file descriptor group, mount, and resource-wait support.

Key responsibilities:
- Allocates/closes `Pgrp` namespace groups and `Rgrp` rendezvous groups.
- Copies namespaces with `pgrpcpy()`, preserving mount order and devmask.
- Inserts/removes mounts in process-group order chains.
- Implements device masking and `canmount()`.
- Duplicates and closes file descriptor groups.
- Handles forced file-group close when a process is killed while stuck closing channels.
- Allocates and frees `Mount` chains.
- Provides `resrcwait()` throttled resource-wait sleep with occasional console warnings.

Important behavior:
- `pgrpcpy()` locks both namespaces for write and uses temporary `Mount.norder` to preserve original order.
- `dupfgrp()` shrinks the new fd table to the current max fd rounded to `DELTAFD`.
- `forceclosefgrp()` moves outstanding channel closes to the close queue to break mount-close deadlocks.
- Masking `Devmnt` is interpreted as blocking all mounts.

Notable risks:
- Namespace copy depends on strict lock ordering and temporary mutation of source mount objects.
