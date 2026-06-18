# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp.h

## Role

Kernel-facing locality group (lgroup/NUMA locality) header. For normal userland it exposes only an opaque `lgrp_mem_policy_info_t`; for `_KERNEL`, `_FAKE_KERNEL`, or `_KMEMUSER` it defines the internal lgroup topology, load, statistics, memory-policy, and platform callback interfaces.

## Structure

- Defines `LGRP_NONE`, root/null/default handles, `NLGRPS_MAX` 64, lgroup load scaling constants, and lpl increment/decrement actions.
- Defines per-lgroup counter and snapshot statistic enums, CPU-bucketed stats storage, `LGRP_KSTAT_NAMES`, and stat access/reset macros.
- Defines core kernel types: `klgrpset_t`, `mnodeset_t`, `lgrp_t`, `lpl_t`, memory-policy and search-scope enums, memory-node cookie, shared-memory policy segments, and memory rename arguments.
- Provides bitset macros for lgroup sets, lgroup/memory helper macros, and CPU/resource membership checks.
- Declares global lgroup topology state and generic/platform functions for init, config, kstats, memory placement, thread placement, topology updates, and platform latency/memory hooks.

## Dependencies And Consumers

Kernel builds include CPU, bitmap, vnode, anon, segment, `lgrp_user.h`, and param headers. The header is consumed by scheduler placement, VM memory allocation, shared memory policy, kstats, processor-set/lgroup topology, and platform NUMA support.

## Important Details

The internal lgroup set representation is a 64-bit mask, so `NLGRPS_MAX` and bit shifts are coupled. Counter stats are bucketed by `CPU->cpu_id` to reduce cache contention, and readers must sum buckets. Several macros are statement macros and depend on globals such as `lgrp_alloc_max`, `lgrp_table`, and `PAGESIZE`.

## Research Notes

Read completely: 642 lines, 19968 bytes.
