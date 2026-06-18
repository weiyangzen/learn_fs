# File Research: sources/os/linux/linux/mm/damon/ops-common.h

Header for shared DAMON operation helpers.

Declares:
- PFN-to-folio helper: `damon_get_folio()`.
- PTE/PMD aging helpers: `damon_ptep_mkold()`, `damon_pmdp_mkold()`.
- Folio aging/access helpers: `damon_folio_mkold()`, `damon_folio_young()`.
- DAMOS scoring helpers: `damon_cold_score()`, `damon_hot_score()`.
- Folio filter helper: `damos_folio_filter_match()`.
- NUMA migration helper: `damon_migrate_pages()`.
- Filter presence helper: `damos_ops_has_filter()`.

This file defines the common interface consumed by `paddr.c` and virtual-address DAMON operations.
