<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wt_internal.h -->
# sources/storage-engines/wiredtiger/src/include/wt_internal.h

## Purpose
Acts as WiredTiger's central internal include umbrella. It establishes C linkage, imports public/config/platform headers, declares generated internal typedefs, and then includes the internal subsystem headers and inline headers in dependency order.

## Important APIs, Types, and Functions
The main exported content is type visibility rather than functions. The generated `dist/s_typedef` block forward-declares and typedefs core structures for block management, btrees, cache, checkpoint, connection/session, cursors, eviction, logging, metadata, reconciliation, transactions, tiered storage, verification, and live restore. For this subset, it introduces `WT_LIVE_RESTORE_FH_META`, `WTI_LIVE_RESTORE_FILE_HANDLE`, `WTI_LIVE_RESTORE_FS`, `WTI_LIVE_RESTORE_FS_LAYER`, `WTI_LIVE_RESTORE_SERVER`, and `WTI_LIVE_RESTORE_WORK_ITEM`, then includes `../live_restore/live_restore.h`.

## Control Flow
There is no runtime control flow. The include order is the control mechanism: platform headers and compiler abstractions come first, then foundational internal headers, subsystem headers, `extern.h` prototypes, build verification, and inline helpers whose comments document prerequisite headers. This ordering lets most `.c` files include one header and receive consistent declarations.

## State and Persistence Behavior
No persistent state is stored here. The header defines the type universe and macro/platform environment that all source files compile against. Including `live_restore.h` here makes live-restore metadata/state functions visible to block, metadata, connection, and cursor code that participate in persistence and startup.

## Dependencies and Integration Points
Depends on `wiredtiger_config.h`, `wiredtiger_ext.h`, OS headers, compiler-specific headers, POSIX/Windows shims, queue/mutex/stat/error/session/connection headers, and a broad set of subsystem headers. `live_restore.h` is integrated midway with other subsystem interfaces before metadata, OS, checkpoint, session, connection, and extern includes.

## Risks and Edge Cases
Because this file is transitively included almost everywhere, any added include or typedef can increase rebuild cost, create dependency cycles, or affect platform portability. The generated typedef block must stay in sync with source declarations. Preprocessor platform choices such as `_WIN32`, Linux, and Apple guards determine what APIs are available across the rest of the codebase.

## Test Signals
The strongest signal is a full WiredTiger build across supported platforms. Live-restore-specific compile signals include references from `block_open.c`, `meta_ckpt.c`, `meta_table.c`, `meta_turtle.c`, `conn_api.c`, and `conn_open.c` resolving through this header. Generated-header drift is caught by WiredTiger distribution/build verification tooling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wt_internal.h -->
