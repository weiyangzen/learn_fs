# File Research: sources/os/linux/linux/mm/hugetlb_cma.c

## Purpose

`hugetlb_cma.c` implements HugeTLB integration with CMA reserved memory. It lets gigantic HugeTLB pages be allocated from per-node CMA areas, supports early boot reservation for CMA-only gigantic pages, parses HugeTLB CMA command-line options, and exposes policy helpers used by the main HugeTLB allocator.

## Major Responsibilities

- Store per-node HugeTLB CMA areas in `hugetlb_cma[]`.
- Parse `hugetlb_cma=` as either a global size or a comma-separated per-node `node:size` list.
- Parse `hugetlb_cma_only=` to force gigantic HugeTLB allocation to use the CMA reservation path.
- Reserve per-node CMA areas during early boot via `hugetlb_cma_reserve()`.
- Allocate and free frozen compound folios from HugeTLB CMA for runtime gigantic-page allocation.
- Provide early bootmem allocation from CMA for hstates that must use CMA before normal runtime allocation is available.
- Validate that CMA-only mode is disabled if no HugeTLB CMA area was configured.

## Allocation and Freeing

`hugetlb_cma_alloc_frozen_folio()` returns a frozen compound folio from a node-local CMA area when available. If allocation is not constrained by `__GFP_THISNODE`, it can fall back across the provided nodemask. Successful allocation marks the folio with `folio_set_hugetlb_cma()` so later freeing returns it to CMA.

`hugetlb_cma_free_frozen_folio()` releases a frozen folio back to its node's CMA area with `cma_release_frozen()`. The main HugeTLB free path calls this when the folio carries the HugeTLB CMA flag.

`hugetlb_cma_alloc_bootmem()` reserves a huge page from a node's CMA area during early boot, optionally falling back to other `hugetlb_bootmem_nodes` when exact-node allocation is not required. It tags the returned `huge_bootmem_page` with `HUGE_BOOTMEM_CMA` and stores the CMA pointer.

## Reservation Setup

`hugetlb_cma_reserve()` is the boot-time CMA declaration path. It first checks that the architecture supplies a nonzero `arch_hugetlb_cma_order()` and warns if the order is not larger than `MAX_PAGE_ORDER`, because this path is intended for gigantic pages. It validates node-specific requests against memory nodes and minimum size, then either reserves the requested per-node sizes or spreads a global request across memory nodes rounded to the gigantic-page size.

The CMA declaration uses `cma_declare_contiguous_multi()` with a name of `hugetlb<nid>`. The "order per bit" argument is `HUGETLB_PAGE_ORDER`, which matters when demotion later returns smaller huge pages to CMA. If all reservations fail, `hugetlb_cma_size` is reset to zero so allocation helpers know CMA is unavailable.

## Policy Helpers

`hugetlb_cma_exclusive_alloc()` reports whether `hugetlb_cma_only` is set. `hugetlb_cma_total_size()` reports whether any CMA reservation was requested/successfully kept. `hugetlb_cma_validate_params()` clears CMA-only mode if there is no CMA area. `hugetlb_early_cma()` tells `hugetlb.c` to allocate gigantic boot pages through CMA when the architecture lacks a huge bootmem allocator and CMA-only mode is active.

This file is compiled behind `CONFIG_CMA`; the companion header provides no-op stubs otherwise.
