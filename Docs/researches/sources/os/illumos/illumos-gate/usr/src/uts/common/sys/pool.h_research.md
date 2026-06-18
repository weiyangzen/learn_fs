# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool.h

## Purpose
Defines the kernel pool framework interface for resource pools, pool IDs, pool state, process binding, configuration, synchronization, and change callbacks.

## Main Interfaces
- Constants:
  - `POOL_DEFAULT`
  - `POOL_MAXID`
  - `POOL_INVALID`
  - `POOL_DISABLED`
  - `POOL_ENABLED`
- Kernel pool structure:
  - `pool_t`: pool ID, process reference count, list linkage, properties, and associated processor set.
- Binding/class constants:
  - `POOL_BIND_PSET`
  - `POOL_BIND_ALL`
  - `POOL_CLASS_UNSET`
  - `POOL_CLASS_INVAL`
- Global kernel state:
  - `pool_count`
  - `pool_default`
  - `pool_state`
  - `pool_buf`
  - `pool_bufsz`
- Lookup:
  - `pool_lookup_pool_by_id()`
  - `pool_lookup_pool_by_name()`
  - `pool_lookup_pool_by_pset()`
- Configuration/binding:
  - `pool_init()`, `pool_status()`, `pool_create()`, `pool_destroy()`
  - `pool_transfer()`, `pool_xtransfer()`
  - `pool_assoc()`, `pool_dissoc()`
  - `pool_bind()`, `pool_do_bind()`, `pool_query_binding()`
  - `pool_get_class()`
  - `pool_pack_conf()`
  - `pool_propput()`, `pool_proprm()`, `pool_propget()`
  - `pool_commit()`, `pool_get_name()`
- Synchronization:
  - `pool_lock()`, `pool_lock_intr()`, `pool_lock_held()`, `pool_unlock()`
  - `pool_barrier_enter()`, `pool_barrier_exit()`
- Change notifications:
  - `pool_event_t`
  - `pool_event_cb_t`
  - `pool_event_cb_register()`
  - `pool_event_cb_unregister()`

## Dependencies And Relationships
Includes types, time, nvpair, procset, and list headers. `pool_pset.h` defines the processor-set backing resource used by pools.

## Research Notes
The state comments appear inverted for `POOL_DISABLED`/`POOL_ENABLED`, but the constants are clearly named. Pool callbacks notify enable, disable, and change events.
