# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hold_page.h

## Role

`hold_page.h` declares platform hooks for validating and optionally locking physical pages while `swrand` maps pages for entropy gathering.

## Key Interfaces and Data

- `PLAT_HOLD_NO_LOCK` checks PFN validity without locking.
- `PLAT_HOLD_LOCK` validates and attempts to exclusively lock the page, returning a `page_t *`.
- `PLAT_HOLD_OK` and `PLAT_HOLD_FAIL` are return values.
- `plat_hold_page(pfn_t, int, page_t **)` performs the validity/lock operation.
- `plat_release_page(page_t *)` unlocks a page previously held with `PLAT_HOLD_LOCK`.

## Dependencies and Use

The header includes `sys/types.h` and `vm/page.h`. It is relevant to platforms and hypervisors where pages may be removed while mapped.

## Research Notes

The comments are the main contract: callers must only release pages returned by successful locking holds.
