# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_pset.h

## Purpose
Defines the kernel processor-set resource component used by pools, including pset properties, CPU properties, binding, transfer, packing, and zone visibility hooks.

## Main Interfaces
- `pool_pset_t`: pset ID, pool membership count, list link, and nvlist properties.
- Global state:
  - `pool_pset_default`
  - `pool_pset_mod`
  - `pool_cpu_mod`
- Lifecycle/configuration:
  - `pool_pset_init()`
  - `pool_pset_enable()`
  - `pool_pset_disable()`
  - `pool_pset_create()`
  - `pool_pset_destroy()`
  - `pool_pset_assoc()`
- Binding/transfer:
  - `pool_pset_bind()`
  - `pool_pset_xtransfer()`
  - `pset_bind_start()`
  - `pset_bind_abort()`
  - `pset_bind_finish()`
- Property operations:
  - `pool_pset_proprm()`, `pool_pset_propput()`, `pool_pset_propget()`
  - `pool_cpu_proprm()`, `pool_cpu_propput()`, `pool_cpu_propget()`
- Serialization/state:
  - `pool_pset_pack()`
  - `pool_pset_enabled()`
- Zone visibility:
  - `pool_pset_visibility_add()`
  - `pool_pset_visibility_remove()`

## Dependencies And Relationships
Kernel-only. Includes CPU partition, procset, nvpair, exacct, time, and list support. Integrates with `pool.h` and zone visibility.

## Research Notes
Modification timestamps distinguish pset changes from CPU changes, which matters for pool configuration snapshots.
