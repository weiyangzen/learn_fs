# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp_topo.c

## Purpose

`lgrp_topo.c` implements topology construction and mutation helpers for locality groups. It builds and updates the lgroup hierarchy based on leaf-to-leaf latency, resource sets, parent/child relations, and configurable topology height limits.

This file complements `lgrp.c`: `lgrp.c` handles lifecycle, CPU/memory events, scheduler load structures, and memory policy, while `lgrp_topo.c` handles the structural algorithms for adding/removing leaves, splitting parents, propagating resource sets, collapsing duplicates, and flattening topology.

## Configuration

Top-level tunables:

- `lgrp_topo_levels`: current topology height limit, default 4.
- `lgrp_collapse_equidist`: collapse only lgroups with same latency and same resources.
- `lgrp_collapse_off`: disables duplicate collapse by default.
- `lgrp_split_off`: disables splitting by default.

Debug builds expose `lgrp_topo_debug` and print helpers for lgroup sets, resource sets, and topology.

## Resource Set Helpers

Resource sets are arrays indexed by `LGRP_RSRC_*`. Helpers include:

- `lgrp_rsets_add()`: OR all resources from one set into another.
- `lgrp_rsets_copy()`: copy resource arrays.
- `lgrp_rsets_delete()`: remove a lgroup ID from one lgroup and optionally its ancestors.
- `lgrp_rsets_empty()`: test whether all resource sets are empty.
- `lgrp_rsets_equal()`: compare all resource sets.
- `lgrp_rsets_member()` and `lgrp_rsets_member_all()`: membership tests.
- `lgrp_rsets_replace()`: replace an lgroup’s resources/latency and optionally shift old contents upward.
- `lgrp_rsets_set()`: initialize all resource classes to a single lgroup ID.

## Topology Mutation

`lgrp_ancestor_delete()` removes a child from its ancestors, decrements child counts, and destroys ancestors that become childless.

`lgrp_consolidate()` merges one non-leaf lgroup into another. It preserves the larger latency, removes empty ancestors of the source, reparents source children to the destination, propagates leaves toward root, and destroys the source lgroup.

`lgrp_collapse_dups()` searches target lgroups for duplicate non-leaf lgroups with identical resource sets, optionally requiring identical latency, and consolidates duplicates.

`lgrp_new_parent()` creates an intermediate parent with a given latency/resource set and inserts it between a child and the child’s old parent.

`lgrp_proprogate()` propagates a new leaf’s resources into a child’s parent if not already present. The misspelling is in the source symbol name.

`lgrp_split()` can split a child away from its parent when sibling leaves have different latency to a newly added leaf. It is gated by `lgrp_split_off`.

## Leaf Addition

`lgrp_lineage_add()` is the core algorithm for placing a new leaf into an existing leaf’s ancestry. It:

1. Gets platform latency between old and new leaves.
2. Walks from the old leaf up toward root.
3. Optionally splits parents when sibling latency differs.
4. Inserts a new intermediate parent if the new latency is less than the current parent latency.
5. Propagates resources upward once placement is found.
6. Enforces the topology height limit by replacing/shift-propagating parent contents when needed.
7. Collapses duplicates among changed lgroups if duplicate collapse is enabled.

`lgrp_leaf_add()` initializes a leaf’s parent as root if needed, sets leaf/root latencies, and adds the new leaf to every other leaf’s lineage and vice versa. It assumes callers hold `cpu_lock`, have preemption disabled, or are running before lgroup initialization.

## Leaf Deletion

`lgrp_leaf_delete()` removes a leaf’s resources from every lgroup that contains it, removes childless ancestors, destroys the leaf, and optionally collapses duplicate lgroups among changed nodes.

## Flattening And Height Limits

`lgrp_topo_flatten()` currently supports flattening to a two-level topology. It destroys non-root non-leaf lgroups and reparents leaves to root, updating root children/leaves and leaf latencies.

Height helper APIs:

- `lgrp_topo_height()`
- `lgrp_topo_ht_limit()`
- `lgrp_topo_ht_limit_default()`
- `lgrp_topo_ht_limit_set()`

`lgrp_topo_ht_limit_set()` caps requested height at `LGRP_TOPO_LEVELS_MAX`.

## Deferred Topology Update

`lgrp_topo_update()` completes topology for leaves whose latency was unavailable when initially added. It handles UMA root setup specially, pauses CPUs while updating delayed leaves, calls `lgrp_mnode_update()` for changed lgroups, and optionally flattens both lgroup and lpl topology when the height limit is 2.

## Concurrency

Topology updates assume strong external synchronization: `cpu_lock`, disabled preemption, or pre-initialization state. Some update paths pause CPUs and must avoid unsafe blocking.

## Dependencies

Depends on `lgrp_table`, `lgrp_root`, `lgrp_create()`, `lgrp_destroy()`, `lgrp_mnode_update()`, `lpl_topo_flatten()`, platform latency callbacks, CPU pause/start infrastructure, and klgrpset bitset helpers.

## Research Notes

Important review points are parent/child count consistency, leaf propagation to root, duplicate collapse safety, height-limit replacement behavior, disabled-by-default split/collapse code paths, and off-by-one iteration over `lgrp_alloc_max` versus passed `lgrp_count`.
