<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wiredtiger_ext.h -->
# sources/storage-engines/wiredtiger/src/include/wiredtiger_ext.h

## Purpose
Defines the public extension-facing WiredTiger API table. Extensions include this header, obtain `WT_EXTENSION_API` through `WT_CONNECTION::get_extension_api`, and call through function pointers rather than linking directly against WiredTiger internals.

## Important APIs, Types, and Functions
`WT_EXTENSION_SPINLOCK` is an opaque wrapper that lets extensions use WiredTiger spin locks. `struct __wt_extension_api` is append-only for ABI compatibility and begins with a private `WT_CONNECTION *conn` field. Its methods cover diagnostics (`err_printf`, `msg_printf`, `strerror`, `map_windows_error`), scratch allocation, collator lookup and comparison, configuration lookup and parser construction, file-system discovery, metadata insert/search/update/remove, deprecated vararg struct packing, streaming pack/unpack operations, version lookup, and extension spin-lock lifecycle/lock/unlock.

## Control Flow
This header contains no executable control flow, but it defines the dispatch table used by extension code. A caller includes the header, asks the connection for an API table, then calls function pointers with the `WT_EXTENSION_API *` and optional `WT_SESSION *` context. The append-only layout is the main control constraint: new functionality must be added at the tail to preserve binary compatibility.

## State and Persistence Behavior
The table can mutate WiredTiger persistent state through the metadata methods and can expose the active `WT_FILE_SYSTEM`. Scratch allocation is short-lived and session-scoped in practice. Pack/unpack routines operate on caller-provided buffers and parser handles. The spinlock object hides WiredTiger lock storage behind an extension-owned placeholder.

## Dependencies and Integration Points
Includes `wiredtiger.h` and is itself included by `wt_internal.h`, so public extension names are visible before internal headers. It integrates with extension modules such as compressors, collators, encryptors, data sources, and storage sources, and with examples referenced by Doxygen snippets. The API is also the boundary that lets dynamically loaded modules avoid direct linkage to core WiredTiger symbols.

## Risks and Edge Cases
The ABI is sensitive to field reordering or insertion before the end of `WT_EXTENSION_API`. Several methods accept varargs or opaque config strings, so caller misuse can cause hard-to-diagnose extension failures. Metadata access from extensions must obey normal WiredTiger locking and lifecycle expectations. `file_system_get` may return `WT_NOTFOUND` during early extension initialization before the file system is established.

## Test Signals
Coverage usually comes from extension example builds and extension-specific tests for compressors/collators/encryptors/storage sources. ABI regressions are signaled by compilation or dynamic-load failures in extension modules and by tests that exercise metadata/config/packing methods through the API table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wiredtiger_ext.h -->
