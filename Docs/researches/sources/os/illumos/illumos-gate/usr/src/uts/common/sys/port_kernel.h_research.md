# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port_kernel.h

## Purpose
Defines kernel-private event-port event/source/cache structures and kernel APIs for associating sources, fd/file objects, sending events, and managing event memory.

## Main Interfaces
- `port_kevent_t`: kernel internal event object, including source, events, flags, pid, object, user cookie, callback, source arg, owning port, and list node.
- Event flags:
  - `PORT_KEV_PRIVATE`
  - `PORT_KEV_CACHED`
  - `PORT_KEV_SCACHED`
  - `PORT_KEV_VALID`
  - `PORT_KEV_DONEQ`
  - `PORT_KEV_FREE`
  - `PORT_KEV_NOSHARE`
- Allocation/callback flags:
  - `PORT_ALLOC_DEFAULT`, `PORT_ALLOC_PRIVATE`, `PORT_ALLOC_CACHED`, `PORT_ALLOC_SCACHED`
  - `PORT_CALLBACK_DEFAULT`, `PORT_CALLBACK_CLOSE`, `PORT_CALLBACK_DISSOCIATE`
- Limits:
  - `PORT_DEFAULT_PORTS`
  - `PORT_MAX_PORTS`
  - `PORT_DEFAULT_EVENTS`
  - `PORT_MAX_EVENTS`
- Source/cache types:
  - `port_source_t`
  - `portfop_cache_t`
  - `port_fdcache_t`
  - `port_ksource_t`
- Kernel APIs:
  - `port_associate_ksource()`
  - `port_dissociate_ksource()`
  - `port_alloc_event()`
  - `port_pollwkup()`
  - `port_pollwkdone()`
  - `port_send_event()`
  - `port_free_event()`
  - `port_init_event()`
  - `port_dup_event()`
  - `port_associate_fd()`
  - `port_dissociate_fd()`
  - `port_associate_fop()`
  - `port_dissociate_fop()`
  - `port_free_event_local()`
  - `port_alloc_event_local()`
  - `port_close_pfd()`

## Dependencies And Relationships
Kernel-only. Includes vnode and list support. `port_fdcache_t` deliberately matches `pollcache_t` field offsets for `pc_lock` and `pc_flag`.

## Research Notes
This header is the kernel API for non-user event sources to interact with event ports. `port_ksource_tab` support lets kernel subsystems associate at port creation time to avoid repeated runtime checks.
