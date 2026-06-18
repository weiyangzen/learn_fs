# File Research: sources/os/linux/linux/mm/hugetlb_cma.h

## Purpose

`hugetlb_cma.h` is the internal interface between core HugeTLB code and the optional HugeTLB CMA implementation. It declares CMA allocation, freeing, boot reservation, and policy helpers when `CONFIG_CMA` is enabled and supplies inline no-op fallbacks when CMA is not built.

## Interface

With `CONFIG_CMA`, it exposes:

- `hugetlb_cma_free_frozen_folio()` to return a frozen HugeTLB CMA folio to CMA.
- `hugetlb_cma_alloc_frozen_folio()` to allocate a frozen compound folio for runtime HugeTLB allocation.
- `hugetlb_cma_alloc_bootmem()` to reserve a boot-time HugeTLB page from CMA.
- `hugetlb_cma_exclusive_alloc()` to report CMA-only allocation mode.
- `hugetlb_cma_total_size()` to report configured/reserved HugeTLB CMA size.
- `hugetlb_cma_validate_params()` to normalize command-line state after parsing.
- `hugetlb_early_cma()` to decide whether a gigantic hstate should allocate boot pages through CMA.

Without `CONFIG_CMA`, all allocation helpers return `NULL`, size returns `0`, exclusive/early-CMA helpers return `false`, and free/validation helpers are empty. This lets `hugetlb.c` call the interface unconditionally while compiling out CMA behavior.
