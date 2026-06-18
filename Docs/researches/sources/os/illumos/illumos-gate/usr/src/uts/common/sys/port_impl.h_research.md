# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_impl.h

## Purpose
Defines private event-port implementation structures for system call dispatch, port queues, alert state, fd associations, file-object watches, VFS/vnode watch state, and file event masks.

## Main Interfaces
- Port syscall codes:
  - `PORT_CREATE`, `PORT_ASSOCIATE`, `PORT_DISSOCIATE`, `PORT_SEND`, `PORT_SENDN`, `PORT_GET`, `PORT_GETN`, `PORT_ALERT`, `PORT_DISPATCH`
  - `PORT_SYS_NOPORT`, `PORT_SYS_NOSHARE`, `PORT_CODE_MASK`
- Limits and flags:
  - `PORT_SHARE_EVENT`
  - `PORT_MAX_LIST`
  - `PORT_SCACHE_SIZE`
  - `PORT_SHASH`
  - `PORT_CLEANUP_DONE`, `PORT_KEV_CACHE`, `PORT_KEV_WIRED`
  - `PORT_FREE_EVENT`
- Kernel structures:
  - `port_alert_t`
  - `port_queue_t`
  - `port_t`
  - `port_control_t`
  - `portget_t`
  - `port_gettimer_t`
  - `portfd_t`
  - `portfop_t`
  - `portfop_vfs_t`
  - `portfop_vfs_hash_t`
  - `portfop_vp_t`
  - `port_kstat_t`
- Queue and port flags:
  - `PORTQ_ALERT`, `PORTQ_CLOSE`, `PORTQ_WAIT_EVENTS`, `PORTQ_POLLIN`, `PORTQ_POLLOUT`, `PORTQ_BLOCKED`, `PORTQ_POLLWK_PEND`
  - `PORT_INIT`, `PORT_CLOSED`, `PORT_EVENTS`
  - `PORTGET_ALERT`
- File-operation event flags and masks:
  - `FOP_FILE_*`
  - `FOP_MODIFIED_MASK`
  - `FOP_ACCESS_MASK`
  - `FOP_ATTRIB_MASK`
  - `FOP_TRUNC_MASK`
  - `FILE_EVENTS_MASK`
- Internal functions:
  - `port_alloc_event_block()`
  - `port_push_eventq()`
  - `port_remove_done_event()`
  - `port_get_kevent()`
  - `port_block()`, `port_unblock()`
  - `port_pcache_remove_fd()`
  - `port_remove_fd_object()`
  - `addfd_port()`, `delfd_port()`

## Dependencies And Relationships
Includes `poll_impl.h`, `port.h`, `port_kernel.h`, vnode, and FEM support. It builds on poll caching for fd events and uses vnode/FEM hooks for file event notification.

## Research Notes
The header is explicitly private and changeable. File watch state has distinct locks: vnode list state is protected by `pvp_mutex`, while most `portfop_t` fields are protected by the source-cache lock.
