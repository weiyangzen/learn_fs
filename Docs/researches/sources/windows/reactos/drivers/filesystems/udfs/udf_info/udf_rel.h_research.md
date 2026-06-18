# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_rel.h

This header defines core UDF filesystem in-memory structures shared by the UDF engine and, conditionally, console/user-mode tooling. It sits above ECMA-167 on-disk definitions and translates UDF disk concepts into driver-maintained state.

Key contents:
- `UDFTrackMap` describes optical/media track ranges, next writable address, packet/session data, addressing workaround flags, and fixed-packet/MRW offset fields.
- `UDFSparingData`, `UDFPartMap`, `UDF_VDS_RECORD`, VRS/VDS constants, and UDF revision constants model partition, sparing, volume descriptor sequence, and recognition state.
- `EXTENT_INFO` pairs user data length with an `EXTENT_MAP`, offset, modification flag, and allocation flags. The extent flags distinguish standard/sequential allocation, preallocation, verification, and 2K compatibility.
- Directory indexing is represented by `DIR_INDEX_HDR`, `DIR_INDEX_ITEM`, and hash entries. `DIR_INDEX_ITEM` caches names, file-entry locations, file-ident flags, system attributes, timestamps, size, allocation size, and optional opened `UDF_FILE_INFO`.
- `UDF_DATALOC_INFO` is the hardlink-aware “actual data location” object. It owns `DataLoc`, `AllocLoc`, `FELoc`, cached file-entry bytes, FE flags, link reference count, directory index, stream-directory info, and the paired NT FCB pointer.
- `UDF_FILE_INFO` is the path/tree instance object. It links an NT FCB, a shared data-location object, cached file-ident bytes, parent/index relationships, reference/open counters, hardlink list links, and an optional FE-list entry.
- `FE_LIST_ENTRY`, `UDF_DATALOC_INDEX`, `UDF_DIR_SCAN_CONTEXT`, `EXT_RELOCATION_ENTRY`, and `UDF_ALLOCATION_CACHE_ITEM` support file-entry lookup, directory scanning, relocation, and allocation descriptor caching.
- `UDF_VERIFY_CTX` stores verification bitmap/list state, lock/event synchronization, waiter/queued counts, and initialization state.

Notable design points:
- The header separates tree identity (`UDF_FILE_INFO`) from physical data identity (`UDF_DATALOC_INFO`) to support hardlinks and delayed cleanup.
- Directory entries are normalized into fixed-size in-memory index items because on-disk file-ident records are variable-size.
- Many memory tags and compile-time debugging/tracking switches are defined here, making this header part of the driver’s allocation and diagnostics contract.
- `UDF_NO_EXTENT_MAP` is a sentinel pointer value, so users of extent maps must distinguish sentinel, null, and valid maps.
