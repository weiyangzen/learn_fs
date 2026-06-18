# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool_pset.c

## Purpose

`pool_pset.c` is the processor-set plugin for the resource pools subsystem. It maps pool resource-component operations onto CPU partitions, processor-set visibility, pset/CPU properties, pset packing, and per-zone CPU visibility behavior.

Read completely: 978 lines.

## Main Responsibilities

- Initializes and maintains the global list of pool-managed processor sets.
- Enables/disables pset support when pools are enabled/disabled.
- Creates and destroys pool processor sets on top of `cpupart_create()` / `cpupart_destroy()`.
- Associates pools with psets and atomically rebinds affected processes through `pool_do_bind()`.
- Transfers named CPU IDs between psets.
- Binds all threads of a process to a target pset after preflight checks.
- Maintains CPU and pset kstat visibility for zones.
- Exposes dynamic and static pset/CPU properties to the common pool layer.
- Packs processor-set and CPU state into exacct groups for pool configuration queries.

## Important Data Structures And Globals

- `pool_pset_list`: list of all `pool_pset_t` objects.
- `pool_pset_default`: the default pset wrapper with ID `PS_NONE`.
- `pool_pset_mod`, `pool_cpu_mod`: modification timestamps for psets and CPU properties.
- `pool_pset_props`: property schema for pset properties such as `pset.name`, `pset.min`, `pset.max`, `pset.load`, and `pset.size`.
- `pool_cpu_props`: property schema for CPU properties such as `cpu.comment`, `cpu.status`, and `cpu.pinned`.

## Control Flow And Algorithms

`pool_pset_init()` allocates the default pset wrapper, links it to `pool_default`, initializes the pset list, and registers a CPU setup callback.

`pool_pset_enable()` refuses to enable pools if non-default CPU partitions already exist. It switches pset visibility from the `ALL_ZONES` token to explicit per-zone visibility, marks the global zone pset as `PS_NONE`, initializes default pset properties, and updates timestamps.

`pool_pset_disable()` requires only the default partition to remain, removes non-system CPU properties, restores all-zone visibility, marks pools disabled for pset checks using `ZONE_PS_INVAL`, and frees default pset properties.

`pool_pset_assoc()` updates a pool's pset pointer, calls `pool_do_bind()` for all processes in that pool, rolls back the pointer on failure, and on success updates zone pset visibility and pset pool reference counts.

`pset_bind_start()` stops weak binding, takes `cpu_lock`, verifies the target pset has CPUs, checks required priority-control privilege, verifies each target process can be controlled by the caller, and asks `cpupart_movable_thread()` whether every thread can move. On success it returns with `cpu_lock` held and weak binding stopped; `pset_bind_finish()` reverses that state.

`pool_pset_pack()` walks psets and their CPUs under `cpu_lock`, generating exacct pset groups containing CPU subgroups plus packed pset property nvlists augmented with dynamic size/load values.

## Dependencies And Integration

- Uses CPU partitioning (`cpupart_*`) for the actual resource set.
- Uses zone visibility and kstat zone membership APIs to control what CPUs and psets zones can see.
- Uses FSS buffers during thread binding because moving a thread can create per-project/per-zone FSS state.
- Cooperates with `pool.c` binding and property dispatch.
- Calls `p_online_internal()` for `cpu.status` property changes.

## Locking And Concurrency

Most entry points require `pool_lock()`. CPU topology and visibility operations require `cpu_lock`. The binding preflight returns with `cpu_lock` held by design so the later bind phase cannot be invalidated by CPU partition changes. CPU setup callbacks run under `cpu_lock` and only act when pset support is enabled.

## Notable Risks And Invariants

- Pools cannot be enabled if arbitrary psets already exist outside the pools model.
- A pset associated with any pool cannot be destroyed.
- Zone-visible CPU state is cached in `zone_t`; `ZONE_PS_INVAL` means pools are disabled for pset visibility purposes.
- `pool_pset_bind()` asserts success because `pset_bind_start()` should have eliminated failure cases.
- Property mutations must update the correct modification timestamp so userspace sees configuration changes.

## Research Relevance

Processor-set pools shape CPU availability and scheduler behavior for zones and projects. This file explains how illumos ties pool configuration to real CPU topology and how zone visibility of CPU resources is enforced.
