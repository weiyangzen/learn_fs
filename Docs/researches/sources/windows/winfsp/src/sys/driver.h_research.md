# File Research: sources/windows/winfsp/src/sys/driver.h

Purpose:
Central internal header for the WinFsp kernel driver. It defines driver-wide macros, dispatch function types, shared data structures, inline helpers, device/file-node contracts, I/O queue and transaction APIs, meta-cache APIs, and compatibility shims used by the sys driver sources.

Major content areas:
- Includes Windows kernel headers (`ntifs.h`, mount/storage/security support) and public WinFsp headers (`winfsp/fsctl.h`, `winfsp/fsext.h`).
- Defines driver names, registry root, security descriptors for control/virtual devices, private status codes (`FSP_STATUS_IOQ_POST`, best-effort post), allocation tags, and I/O increment.
- Provides debug, trace, enter/leave, and return macros that wrap filesystem critical-region entry, top-level IRP management, device references, logging, asynchronous queue posting, and IRP completion.
- Declares all major dispatch routines, I/O prepare/complete callbacks, Fast I/O callbacks, cache-manager callbacks, and resource propagation helpers.

Key structures and protocols:
- `FSP_SILO_GLOBALS` stores per-silo control devices, MUP provider handle, MUP device name buffer, and initialization flags.
- Process-buffer APIs cap shared buffers at `FspProcessBufferSizeMax` (64 KiB) and provide acquire/release/collect primitives used by read/write/query-directory paths.
- IRP context helpers pack a request pointer plus low-bit flags into `Irp->Tail.Overlay.DriverContext[2]`; separate helpers access current request, ordinary flags, and propagated top-level IRP flags.
- `FSP_QEVENT` implements a synchronization-event-like primitive using `KQUEUE`, a dummy entry, and a spin lock, giving LIFO wait behavior and thread-count limiting.
- `FSP_IOQ` models WinFsp's pending/process/retried IRP queue with cancel-safe queues, pending capacity, timeout handling, stopped state, and process buckets.
- `FSP_META_CACHE` is the generic cache behind security descriptors, directory info, stream info, and EA buffers. It tracks timeout, capacity, max item size, item indexes, list state, and hash buckets.
- `FSP_FSCTL_TRANSACT_REQ_HEADER` prefixes user-mode transaction requests with finalizer context, optional response/work item, and aligned request storage. `FspIopRequestContext` exposes per-request context slots used heavily by asynchronous completions.

Device model:
- Device extension kinds identify fsctl, fsmup, fsvrt, and fsvol objects.
- `FSP_DEVICE_EXTENSION` is the base with spin lock, refcount, kind, timer emulation, and delete state.
- `FSP_FSVOL_DEVICE_EXTENSION` is the main mounted volume state: links to fsctl/fsvrt/fsvol devices, swap VPB, volume params, provider, volume prefix, I/O queue, security/dir/stream/EA meta caches, expiration work, delete/rename resources, context tables, volume info cache, notify state, statistics, and filesystem-extension data.
- `FSP_FSVRT_DEVICE_EXTENSION` tracks virtual volume identity, sector size, mount mutex, mountdev state, persistent flag, unique ID, and mount point.
- `FSP_FSMUP_DEVICE_EXTENSION` tracks prefix/class tables for UNC routing.

File object model:
- `FSP_FILE_NODE_NONPAGED` holds resources, section object pointers, nonpaged info spin lock, and meta-cache item indexes.
- `FSP_FILE_NODE` is the FCB-like object: advanced FCB header, ref/open/handle/share state, active/context-table links, file name, cached basic/file info, change numbers for file/security/dir/stream/EA metadata, file lock, oplock state, cache-manager TLS flags, fsvol backpointer, user context, index number, directory/root flags, stream main-file relation, and inline filename buffer.
- `FSP_FILE_DESC` is the per-open CCB-like object: file node, second user context, granted access and per-handle flags, directory query pattern/marker/cache hint, EA query index/change count, and stream main-file handle/object.
- Inline acquisition/release macros standardize main, paging I/O, and full file-node locking, including owner release for asynchronous operations.

Important helper declarations:
- File and EA name validation/upcase/compare/match helpers.
- Registry, GUID, security, mount manager, mountdev, MUP, volume, notification, oplock, cache-manager, safe-MDL, work-item, and IRP hook helpers.
- File-node cache functions for security, directory info, stream info, and EA buffers map to the generic meta-cache dereference routine.
- Volume readiness, notify locking, context table locking, rename/delete resource helpers, and statistics macros.

Compatibility shims:
- Redefines `RtlEqualMemory` for environments where it maps to unavailable `memcmp`.
- Defines local `FSP_FILE_STAT_INFORMATION`, `FSP_FILE_STAT_LX_INFORMATION`, and `FSP_ATOMIC_CREATE_ECP_CONTEXT` for WDKs missing these types or flags.
- Provides multi-version declarations such as `FSP_MV_CcCoherencyFlushAndPurgeCache`.

Dependencies:
- This header is consumed by the WinFsp sys driver C files and depends on public WinFsp FSCTL/FSEXT ABI definitions.
- It is tightly coupled to Windows kernel resource, IRP, file-object, cache-manager, oplock, MUP, mountmgr, and FSRTL notification APIs.
- It declares cross-module interfaces rather than implementing most subsystem behavior.

Research notes:
- This is the most important file for understanding WinFsp kernel-driver invariants. Most source files rely on its enter/leave macros for correct IRP completion and device-reference lifetime.
- The file establishes the core mapping from Windows FSD concepts to WinFsp's user-mode transaction architecture: file nodes/descriptors, per-volume I/O queues, process buffers, and meta caches.
- Any change to `DriverContext` packing, request header layout, file-node lock ownership, or device extension layout would affect many asynchronous code paths.
