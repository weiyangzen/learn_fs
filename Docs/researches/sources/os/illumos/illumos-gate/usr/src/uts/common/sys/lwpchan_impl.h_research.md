# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwpchan_impl.h

## Role

Private process cache for translating process-shared LWP synchronization object virtual addresses into logical `lwpchan_t` addresses.

## Structure

Defines CV/MP pool IDs, initial and maximum hash bits, `lwpchan_entry_t`, hash bucket structure, process-level `lwpchan_data_t`, and exported cache maintenance functions `lwpchan_delete_mapping()` and `lwpchan_destroy_cache()`.

## Dependencies And Consumers

The header is consumed by kernel LWP synchronization and VM mapping teardown/exec/exit paths. It relies on `proc_t`, `caddr_t`, `lwpchan_t`, `kmutex_t`, and integer typedefs from including context.

## Important Details

The cache avoids repeated `as_getmemid()` calls for shared sync objects. Resizing requires acquiring all bucket locks; a comment notes `p->p_lcp` cannot change while any bucket lock is held.

## Research Notes

Read completely: 94 lines, 3279 bytes.
