<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/buf_inline.h -->
# sources/storage-engines/wiredtiger/src/include/buf_inline.h

## Purpose
Provides inline buffer management helpers for `WT_ITEM` objects and session scratch buffers. The functions normalize allocation, growth, content assignment, initialization, and release while preserving WiredTiger's convention that `WT_ITEM.data` can point either inside owned memory or at external data before a grow operation copies it locally.

## Important APIs, Types, and Functions
`__wt_buf_grow` ensures the buffer owns enough memory and accounts for `data` pointing at an offset inside `mem`. It delegates allocation/copying to `__wt_buf_grow_worker`.

`__wt_buf_extend` grows exponentially for repeated appends or extension-style workloads.

`__wt_buf_init` creates an empty buffer of at least a requested size without copying external data. `__wt_buf_initsize` also sets the logical data size.

`__wt_buf_set`, `__wt_buf_set_and_grow`, and `__wt_buf_setstr` set the logical contents before forcing ownership and capacity.

`__wt_buf_free` frees owned memory and clears the item. `__wt_scr_free` returns scratch buffers to the session cache or frees oversized scratch memory when the session scratch budget would be exceeded.

## Control Flow
The grow helpers set up `WT_ITEM` metadata so the worker can determine whether to allocate, reallocate, or copy referenced data. `__wt_buf_extend` doubles the current memory size when possible. Scratch free clears `*bufp`, then either releases the backing memory or accumulates its memory size in `session->scratch_cached`, clears active data fields, and removes `WT_ITEM_INUSE`.

## State and Persistence Behavior
All state is transient process memory. The file mutates `WT_ITEM.mem`, `memsize`, `data`, `size`, flags, and `session->scratch_cached`. No filesystem state is persisted, but these helpers are used when constructing disk images, keys, values, config strings, and temporary decode buffers elsewhere.

## Dependencies and Integration Points
Depends on `WT_ITEM`, `WT_SESSION_IMPL`, `WT_DATA_IN_ITEM`, `WT_PTRDIFF`, `WT_MAX`, `__wt_buf_grow_worker`, `__wt_free`, and session scratch-cache limits. It integrates broadly with cell packing/unpacking, row-key construction, schema/config handling, reconciliation image building, and cursor key/value buffers.

## Risks and Edge Cases
Callers must understand whether `WT_ITEM.data` references external memory or owned memory. `__wt_buf_grow` includes offset data in its capacity test, preventing callers from underallocating when appending to a slice inside the buffer. `__wt_buf_setstr` includes the trailing NUL in `size`, which is intended for string buffers but not arbitrary binary values. Scratch caching relies on `WT_ITEM_INUSE` discipline; freeing a buffer still in use would create aliasing bugs.

## Test Signals
Indirect coverage comes from tests that grow cursor buffers, decode prefix-compressed keys, build reconciliation images, process configuration strings, and exercise session scratch reuse under memory pressure. Memory sanitizer or diagnostic runs should catch use-after-free and stale scratch-buffer reuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/buf_inline.h -->
