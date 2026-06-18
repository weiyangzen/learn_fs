# File Research: sources/os/linux/linux/mm/damon/modules-common.c

Shared helper implementation for DAMON module consumers.

Primary function:
- `damon_modules_new_paddr_ctx_target()` allocates a new DAMON context, selects `DAMON_OPS_PADDR`, creates a target, adds the target to the context, and returns both pointers.

Failure handling:
- Destroys the context if selecting physical-address ops fails.
- Destroys the context if target allocation fails.
- Returns `-ENOMEM` for allocation failures and `-EINVAL` for missing/invalid paddr ops.

Used by DAMON_RECLAIM and DAMON_LRU_SORT to avoid duplicating context/target setup.
