# sources/storage-engines/wiredtiger/src/include/btmem.h

## Purpose
This header is the central in-memory btree/page model. It defines disk page headers, read flags, history-store record formats, reconciliation replacement state, page modification metadata, page/ref/update/insert structures, split-generation protection, and verification context.

## Important APIs, Types, And Functions
Important persistent and runtime types include `WT_PAGE_HEADER`, `WT_ADDR`, `WT_OVFL_REUSE`, `WT_SAVE_UPD`, `WT_PAGE_BLOCK_META`, `WT_PAGE_DISAGG_INFO`, `WT_MULTI`, `WT_OVFL_TRACK`, `WT_PAGE_MODIFY`, `WT_PAGE_INDEX`, `WT_PAGE`, `WT_PAGE_DELETED`, `WT_ADDR_COPY`, `WT_REF`, `WT_ROW`, `WT_COL`, `WT_IKEY`, `WT_UPDATE`, `WT_UPDATE_VALUE`, `WT_UPDATE_VECTOR`, `WT_INSERT`, `WT_INSERT_HEAD`, and `WT_VERIFY_INFO`. Key macros define read flags, HS key/value formats and table configs, page/ref/update states, page flags, update flags, read generations, row/column accessors, insert-list helpers, and split-generation enter/leave wrappers.

## Control Flow
The declarations encode the control model used elsewhere. Readers use `WT_REF` states plus hazard pointers to move pages from disk to memory and protect them. Eviction transitions refs through `WT_REF_LOCKED` and either back to `WT_REF_MEM` or to `WT_REF_DISK`. Internal page splits atomically swap `WT_PAGE_INDEX` pointers, and readers must enter `WT_GEN_SPLIT` before examining indexes. Updates form per-key chains, and visibility code interprets transaction ids, timestamps, durable timestamps, and prepare states. Reconciliation records replacement blocks in `WT_PAGE_MODIFY` as either one address/disk image or multiple `WT_MULTI` entries with unresolved saved updates.

## State And Persistence Behavior
`WT_PAGE_HEADER` is an on-disk format with fixed size, page type, flags, version, recno, write generation, memory size, and entry/data counts. HS format constants define table keys as btree id, key, start timestamp, and counter, and values as stop durable timestamp, durable timestamp, update type, and value. In-memory state includes dirty bytes, update bytes, newest commit timestamp, rec max transaction/timestamp, checkpoint cleanup state, instantiated fast-truncate updates, read generations, cache create/evict pass generations, and disaggregated page metadata. Update and page-delete prepare states require strict memory ordering.

## Dependencies And Integration Points
This header is included across btree search, cursor, reconciliation, eviction, checkpoint, history-store, rollback-to-stable, verify, block manager, and disaggregated storage code. `evict_walk.c` depends on read flags, `WT_REF`, `WT_PAGE`, `WT_PAGE_MODIFY`, read generation constants, and update-candidate state. `hs_cursor.c` depends on HS formats, `WT_UPDATE`, `WT_UPDATE_VALUE`, and update vectors. `block.h` relies on `WT_PAGE_HEADER_SIZE` and page block metadata.

## Risks
The highest risks are ABI/disk-format drift, unsafe direct access to obscured volatile fields, missing generation protection while reading internal indexes, incorrect ref-state transitions, prepare-state memory ordering bugs, dangling fast-truncate `page_del` state, update-chain memory accounting mistakes, and failure to preserve previous reconciliation choices via `WT_UPDATE_SELECT_FOR_DS`. Many fields are deliberately shared and approximate; callers must know which values are advisory and which require locks.

## Test Signals
Use static size/layout assertions, endian page-header tests, ref-state transition stress with hazard pointers, split-generation concurrency tests, prepared transaction visibility tests, fast-truncate instantiate/commit/rollback tests, reconciliation with single and multi-block replacements, HS restore tests, update-vector growth tests, eviction read-generation tests, disaggregated delta metadata tests, and sanitizer runs for update/insert memory ownership.
