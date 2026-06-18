# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp_user.h

## Role

Public/user ABI definitions for lgroup discovery, affinity, latency, and memory-size queries. It also defines the kernel-visible snapshot layout used to transfer lgroup hierarchy state to userland.

## Structure

- Defines current lgroup interface version 2 and lgroup syscall subcodes for meminfo, generation, version, snapshot, affinity, latency, and home queries.
- Defines resource identifiers (`CPU`, `MEM`), affinity values, content/view enums, latency query type, memory-size type/flags, and `lgrp_affinity_args_t`.
- Defines `lgrp_info_t` and `lgrp_snapshot_header_t` with pointers to per-lgroup info, CPU arrays, bitsets, parent/child/resource sets, and latency matrix.
- Under `_SYSCALL32`, provides ILP32-compatible `lgrp_info32_t` and `lgrp_snapshot_header32_t`.
- For non-kernel consumers, declares the `lgrp_*` public library/API functions.

## Dependencies And Consumers

Includes `sys/lgrp.h`, procset, processor, pset, integer, and type headers. Userland consumers use it through liblgrp-style calls; kernel syscall handlers and compatibility code use the concrete snapshot and 32-bit layouts.

## Important Details

`LGRP_CONTENT_HIERARCHY` aliases `LGRP_CONTENT_ALL` for compatibility. Snapshot structures contain native pointers in the LP64 layout and explicit `caddr32_t` fields in the ILP32 layout. `lgrp_mem_size_t` is `longlong_t`, while the 32-bit snapshot stores page counts as `uint32_t`.

## Research Notes

Read completely: 295 lines, 8298 bytes.
