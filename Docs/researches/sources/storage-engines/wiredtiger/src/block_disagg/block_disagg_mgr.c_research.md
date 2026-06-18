# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_mgr.c

## Purpose
Defines the disaggregated block manager facade exposed through `WT_BM`. It adapts WiredTiger's normal block-manager calls to page-log backed remote storage, wires the vtable, owns block-manager open/close/free/write/read/checkpoint dispatch, and decides whether a file handle belongs to the disaggregated manager.

## Important APIs, types, and functions
- `__wt_block_disagg_manager_open` allocates `WT_BM`, marks it remote, wires methods, strips `file:`, and opens a `WT_BLOCK_DISAGG`.
- `__wt_block_disagg_manager_owns_object` currently selects this manager for `file:` handles whose btree has a page log.
- Static adapters include `__bmd_write`, `__bmd_free`, `__bmd_close`, `__bmd_stat`, `__bmd_get_page_ids`, `__bmd_addr_invalid`, and `__bmd_write_size`.
- `__bmd_method_set` binds disaggregated implementations and unsupported stubs into the `WT_BM` method table.
- Important types are `WT_BM`, `WT_BLOCK_DISAGG`, `WT_PAGE_LOG_HANDLE`, `WT_BLKCACHE`, and `WT_DSRC_STATS`.

## Control flow
Open allocates a `WT_BM`, marks `is_remote`, calls `__bmd_method_set`, strips the URI prefix, and delegates to `__wti_block_disagg_open`. On failure it uses the vtable close path for cleanup. Write calls capacity throttling with checkpoint or eviction throttle tags, then delegates to `__wti_block_disagg_write`. Free delegates to `__wti_block_disagg_page_discard` and removes the address from the block cache when configured. Close delegates to `__wti_block_disagg_close` and frees the `WT_BM`.

`__bmd_get_page_ids` asserts a disaggregated btree, warns and returns success if the page-log hook is absent, otherwise asks the page-log handle for all page IDs at a checkpoint LSN.

## State and persistence behavior
This file owns no persistent format directly, but it is the vtable boundary for all persistence calls. It marks block managers as remote, routes writes and checkpoints into page-log storage, routes discard into page-log discard plus block-cache invalidation, and reports size/statistics from disaggregated checkpoint metadata. `can_truncate` always returns false because there is no local file tail to reclaim.

## Dependencies and integration points
The file integrates the block-disaggregated modules with the generic btree/block-manager layer. It references address validation/string helpers, checkpoint handlers, read/read-multiple handlers, write/write-size handlers, size/stat handlers, and unsupported operation stubs. It also integrates with capacity throttling and `WT_BLKCACHE` eviction of freed remote blocks.

## Risks and edge cases
- `__wt_block_disagg_manager_owns_object` is intentionally broad and keyed on page-log presence; incorrect page-log setup can route a file to the wrong manager.
- Several normal block-manager methods point to no-op stubs, so callers must tolerate unsupported local-file semantics.
- `__bmd_get_page_ids` silently succeeds when the page-log provider lacks the hook, which may hide missing functionality unless verbose warnings are monitored.
- The vtable has to stay in sync with `WT_BM` expectations; missing hooks such as compaction rewrite/progress can matter for generic btree operations.

## Test signals
Tests should cover manager selection, open/close reference cleanup, write throttling dispatch, free plus block-cache invalidation, page-ID fetch with and without provider support, and generic block-manager operations against disaggregated handles. Integration tests should validate every installed vtable slot used by checkpoint, eviction, verify, compact, and cursor reads.
