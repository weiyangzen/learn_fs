# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/fsal_up.c

## Purpose

`fsal_up.c` implements Gluster FSAL upcall processing. It translates GFAPI inode invalidation and optional lease recall events into Ganesha FSAL up-vector calls, either through an older polling thread or through the newer GFAPI upcall registration callback. The complete 368-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `up_process_event_object`, `GLUSTERFSAL_UP_Thread`, and `gluster_process_upcall`. Important types include `struct glusterfs_fs`, `struct glfs_upcall`, `struct glfs_upcall_inode`, optional `struct glfs_upcall_lease`, `struct glfs_object`, `struct fsal_up_vector`, and `struct gsh_buffdesc`.

## Control Flow

`up_process_event_object` extracts a GFAPI object handle, prepends the volume UUID to build the FSAL cache key, and dispatches based on the event reason. Inode invalidation calls `invalidate_close` with `FSAL_UP_INVALIDATE_CACHE`; optional lease recall calls `delegrecall`. `GLUSTERFSAL_UP_Thread` registers as an RCU thread, waits for upcall readiness, polls `glfs_h_poll_upcall`, handles retryable `ENOMEM`, decodes inode invalidate or lease recall payloads, processes object/parent/old-parent objects, frees callbacks, and exits when `destroy_mode` is set. `gluster_process_upcall` performs the same decode/dispatch for registered callback mode and frees the callback before returning.

## State and Persistence Behavior

The file owns no persistent data. It observes `gl_fs->destroy_mode`, `up_poll_usec`, GFAPI context, and up-vector readiness. Its runtime effect is cache and delegation state invalidation in Ganesha, keeping MDCACHE and client delegation state coherent with backend Gluster changes.

## Dependencies and Integration Points

Dependencies include GFAPI upcall APIs, Gluster internal state, FSAL up-vector interfaces, SAL functions, Userspace RCU thread registration, logging, and optional Gluster delegation support. It is started/registered by `export.c` when upcalls are enabled and is also called directly by `ds.c` after DS writes.

## Risks and Edge Cases

Event enum naming differs between poll and callback APIs (`GLFS_UPCALL_*` versus `GLFS_EVENT_*`), so dispatch mappings must match the compiled GFAPI version. The polling loop aborts on persistent `ENOMEM`, treats `ENOTSUP` as event-level exit, and can leak responsiveness if callbacks are repeatedly null. Parent and old-parent invalidations are best-effort and errors other than no-entry are logged. Callback mode waits for upcall readiness inside the callback, so readiness ordering matters.

## Test Signals

Test signals include synthetic inode invalidation for object, parent, and old parent handles; optional lease recall; missing/null event args; GFAPI handle extraction and volume-id failures; polling-thread shutdown through `destroy_mode`; `ENOMEM` retry behavior; `ENOTSUP` handling; callback-mode cleanup; direct invalidation after pNFS DS write; and MDCACHE invalidation observed by subsequent NFS LOOKUP/GETATTR.
