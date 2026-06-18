# File Research: sources/os/plan9/plan9/sys/src/9/port/pgrp.c

Implements process group support for namespaces, rendezvous groups, file descriptor groups, mount duplication, and resource-wait throttling.

Key responsibilities:
- `newpgrp`, `closepgrp`: allocate/free namespace groups and all mount heads.
- `newrgrp`, `closergrp`: allocate/free rendezvous groups.
- `pgrpnote`: posts a note to all non-kernel processes sharing a note id.
- `pgrpcpy`: copies a process namespace while preserving parent mount-id allocation order.
- `newmount`, `mountfree`, `pgrpinsert`: allocate/free ordered mount chains.
- `dupfgrp`, `closefgrp`, `forceclosefgrp`: duplicate and tear down file descriptor groups.
- `resrcwait`: sleep briefly during resource exhaustion and rate-limit console complaints.

Important behavior:
- `pgrpcpy` builds a temporary order chain of parent mounts, then allocates copied mount ids in parent order while holding `mountid`.
- `closefgrp` sets `up->closingfgrp` so `forceclosefgrp` can move remaining channels to the close queue if a kill interrupts a deadlocked close path.
- `closepgrp` invalidates `pgrpid`, closes mount source channels, frees mount chains, and drops mount heads under namespace/debug locks.

Role:
- Provides core process-shared namespace/fd/rendezvous state used by `rfork`, process exit, bind/mount, and `/proc`.
