# File Research: sources/os/bsd/netbsd-src/sys/sys/radixtree.h

## Purpose
Declares a generic 64-bit-key radix tree with node lookup/update, gang lookup, and tag support.

## Main API
- Structure: `struct radix_tree` with root and height.
- Kernel subsystem functions: `radix_tree_init`, `radix_tree_await_memory`.
- Tree lifecycle: `radix_tree_init_tree`, `radix_tree_fini_tree`, `radix_tree_empty_tree_p`.
- Node operations: `radix_tree_insert_node`, `radix_tree_replace_node`, `radix_tree_remove_node`, `radix_tree_lookup_node`, `radix_tree_gang_lookup_node`, reverse gang lookup.
- Tags: `radix_tree_tagmask_t`, `RADIX_TREE_TAG_ID_MAX`, `radix_tree_get_tag`, `set_tag`, `clear_tag`, tagged gang lookup, reverse tagged lookup, `radix_tree_empty_tagged_tree_p`.

## Dependencies
Uses kernel/standalone `sys/types.h` or userland boolean/integer headers.

## Risks and Notes
Tag IDs are limited by `RADIX_TREE_TAG_ID_MAX`. Kernel users may need to handle memory pressure via `radix_tree_await_memory` after failed insertions.
