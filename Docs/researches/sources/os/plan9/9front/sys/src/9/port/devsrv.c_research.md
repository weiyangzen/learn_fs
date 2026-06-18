# File Research: sources/os/plan9/9front/sys/src/9/port/devsrv.c

Purpose: Implements `#s`, the service registry for posting open channels by name so other processes can open them later.

Key logic:
- Uses `Srv` entries for posted channels and `Board` directories for hierarchical lease boards.
- Root board starts as `#s`; `clone` creates a lease board with a generated numeric name and qid type `Qlease`.
- Creating a file reserves a service name; writing an fd stores the referenced channel after rejecting auth files and duplicate posts.
- Opening a service replaces the registry channel with the posted channel after mode and permission checks.
- Closing a lease board marks it closed and closes all posted service channels under it.
- `srvremove` removes service entries owned by the caller or eve; `srvwstat` can rename/change owner/mode subject to conflict checks.
- `srvrenameuser` updates board and service owners globally.

Dependencies and integration:
- Uses `fdtochan`, channel refcounting, path service names, `RWLock`, and Plan 9 device generation.

Risks and notes:
- Posted channels must match requested mode unless they are `ORDWR`.
- Lease boards can persist with zero refs while children exist, then are pruned upward when closed and childless.
- `clone` is reserved and cannot be used as a service or board name.
