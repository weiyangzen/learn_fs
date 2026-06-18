# File Research: sources/os/linux/linux/mm/mempolicy.c

## Purpose

Implements Linux NUMA memory policy: process policies, VMA policies, shared tmpfs/shmem policies, policy-aware allocation, policy-driven migration, NUMA balancing placement checks, weighted interleave, and the user-facing `set_mempolicy`, `get_mempolicy`, `mbind`, `migrate_pages`, and `set_mempolicy_home_node` syscalls.

## Policy Model

Supported policy modes include:

- `MPOL_DEFAULT`
- `MPOL_LOCAL`
- `MPOL_PREFERRED`
- `MPOL_PREFERRED_MANY`
- `MPOL_BIND`
- `MPOL_INTERLEAVE`
- `MPOL_WEIGHTED_INTERLEAVE`

The system default policy is local allocation. Per-task policy applies to most process-context allocations. VMA policy overrides task policy for faults. Shared policies persist on backing objects such as tmpfs files.

Policy objects are slab-allocated, refcounted, and freed through RCU because some speculative mmap users can observe policies outside normal mmap lock boundaries.

## Policy Construction and Rebinding

`mpol_new()` validates mode, flags, and nodemask shape. `mpol_set_nodemask()` contextualizes nodemasks against cpuset and online memory nodes, preserving user nodemasks for static/relative modes where needed.

Rebinding paths include:

- `mpol_rebind_task()`
- `mpol_rebind_mm()`
- `mpol_rebind_policy()`

They preserve static, relative, or cpuset-remapped semantics when cpusets change. VMA rebinding is protected by `mmap_write_lock()` and VMA write locking.

## Syscall Paths

`set_mempolicy()` uses `do_set_mempolicy()` to install a task policy under `task_lock()`.

`get_mempolicy()` can report the current policy, allowed mems, next interleave node, weighted interleave node, or the actual node of a page at an address.

`mbind()` uses `do_mbind()` to:

1. Validate range, flags, and nodemask.
2. Build a new policy.
3. Queue misplaced folios when strict or migration flags are requested.
4. Split/merge VMAs and replace VMA policies.
5. Migrate queued folios using policy-aware target allocation.
6. Return strict placement errors when requested.

`migrate_pages()` validates permissions and cpuset access, then moves pages between source and destination node masks while preserving relative node layout when possible.

`set_mempolicy_home_node()` sets `home_node` for existing `MPOL_BIND` or `MPOL_PREFERRED_MANY` VMA policies.

## Page Scanning and Migration

`queue_pages_range()` walks page tables with `mm_walk_ops`, checking whether present folios are on required nodes and optionally isolating them for migration.

It handles:

- PTE mappings.
- THP/PMD mappings.
- hugetlb mappings.
- migration entries.
- strict non-migration checks.
- VMA holes unless `MPOL_MF_DISCONTIG_OK` is set.
- shared folio avoidance unless `MPOL_MF_MOVE_ALL` is set.

Migration target allocation is policy-aware via `alloc_migration_target_by_mpol()`, including hugetlb and large folio cases.

## Allocation-Time Policy

Central allocation helpers include:

- `policy_nodemask()`
- `alloc_pages_mpol()`
- `folio_alloc_mpol_noprof()`
- `vma_alloc_folio_noprof()`
- `alloc_frozen_pages_noprof()`
- `alloc_pages_noprof()`
- `folio_alloc_noprof()`
- `alloc_pages_bulk_mempolicy_noprof()`
- `mempolicy_slab_node()`

`policy_nodemask()` translates policy into a preferred node and optional allocation nodemask. Bind policy applies only for suitable zones, preferred-many uses a two-pass preferred-then-fallback allocation, and interleave policies select nodes by current task counters or address-derived interleave index.

THP allocation avoids broad fallback for non-interleave policies when the current or preferred node is allowed, because remote THP can be worse than smaller local pages.

## Interleave and Weighted Interleave

Classic interleave chooses nodes round-robin by task state or page offset. Weighted interleave uses per-node weights from `wi_state`.

Weighted interleave state is RCU-protected and updated under `wi_state_lock`. It supports:

- Manual per-node weights through sysfs.
- Automatic weights derived from memory-tier performance coordinates via `mempolicy_set_node_perf()`.
- GCD reduction of bandwidth-derived weights.
- Bulk allocation batching by full weighted rounds.

Sysfs creates `/sys/kernel/mm/mempolicy/weighted_interleave`, an `auto` knob, and per-node weight files. Node hotplug adds/removes per-node files.

## Shared Policy Storage

Shared policies are stored in a red-black tree of `struct sp_node` ranges protected by `shared_policy.lock`.

Important functions:

- `mpol_shared_policy_init()`
- `mpol_shared_policy_lookup()`
- `mpol_set_shared_policy()`
- `mpol_free_shared_policy()`
- `shared_policy_replace()`

Range replacement deletes, trims, splits, or inserts policy nodes while preserving non-overlapping file page ranges.

## NUMA Balancing

Under `CONFIG_NUMA_BALANCING`, this file implements:

- `folio_can_map_prot_numa()`
- `change_prot_numa()`
- boot parsing for `numa_balancing=`
- `mpol_misplaced()`

`mpol_misplaced()` decides whether a faulted folio should migrate toward a policy target or the accessing CPU, honoring `MPOL_F_MOF`, `MPOL_F_MORON`, interleave placement, bind/preferred-many masks, and node distance/zonelist choices.

## Tmpfs Policy Parsing

Under `CONFIG_TMPFS`, `mpol_parse_str()` parses mount option policies in the form `<mode>[=<flags>][:<nodelist>]`, and `mpol_to_str()` formats policies for display. It supports static and relative flags and preserves user nodemasks for contextualization.

## Initialization

`numa_policy_init()` creates policy caches, initializes per-node preferred policies, sets an interleave policy for init across memory nodes of sufficient size, and enables or disables automatic NUMA balancing according to config and boot parameters.

## Locking and Lifetime

- Task policies are protected by `task_lock()`.
- VMA policy changes require mmap write locking and VMA write locks.
- Shared policy trees use rwlocks.
- Weighted interleave updates use `wi_state_lock` plus RCU.
- `mpol_put_task_policy()` clears a task pointer before dropping the final ref to avoid allocator instrumentation touching freed policy state.

## Risks and Invariants

Important invariants include valid nodemask/cpuset intersections, correct refcount ownership for shared policies, VMA range continuity checks for `mbind`, avoiding migration of shared/pinned/dirty unsuitable folios, and preserving policy semantics across cpuset rebinding. Weighted interleave must keep RCU readers safe while sysfs and performance updates replace state.
