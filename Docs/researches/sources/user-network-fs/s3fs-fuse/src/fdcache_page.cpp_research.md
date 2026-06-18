# sources/user-network-fs/s3fs-fuse/src/fdcache_page.cpp

Purpose: Implements `PageList`, the range map that records which byte ranges of a cache file are loaded from S3 and/or modified locally. It also serializes/deserializes that state, plans multipart download/upload ranges, and validates sparse cache files against sidecar stats.

Important APIs and functions: Utility compressors merge adjacent `fdpage` ranges and split large modified ranges by multipart size. Public methods include `Init`, `Size`, `Resize`, `Compress`, `IsPageLoaded`, `SetPageLoadedStatus`, `FindUnloadedPage`, `GetTotalUnloadedPageSize`, `GetUnloadedPages`, `GetPageListsForMultipartUpload`, `GetNoDataPageLists`, `BytesModified`, `IsModified`, `ClearAllModified`, `Serialize`, `Deserialize`, `Dump`, and `CompareSparseFile`. Static helpers use `SEEK_DATA`/`SEEK_HOLE` and zero scanning for cache validation.

Control flow: Mutations split ranges at boundaries via `Parse`, update flags, and compress adjacent compatible ranges. Reads ask for unloaded ranges and mark them loaded after downloads. Writes mark ranges `LOAD_MODIFIED` or `MODIFIED`. Mixed multipart planning compresses by modified status, downloads too-small neighboring areas to satisfy S3 minimum part size, and emits upload/copy page lists split by max part size. Serialization writes a header `<inode>:<size>` followed by `offset:bytes:loaded:modified` rows; deserialization supports old headers without inode and old rows without modified flag.

State and persistence behavior: `pages` is the in-memory ordered range list; `is_shrink` keeps truncation dirty even if no range is marked modified. Persistent state is written through `CacheFileStat::OverWriteFile`. Deserialization rejects inode mismatches and size mismatches to avoid applying stale sidecars to a different cache file.

Dependencies and integration points: Used heavily by `FdEntity` for read/write/flush/load decisions and by `FdManager::CheckAllCache` for consistency diagnostics. Depends on `CacheFileStat`, sparse-file lseek behavior, logger macros, and `string_util` conversion helpers.

Risks: Off-by-one and size-vs-end mistakes are high impact because ranges drive both data downloads and remote upload part selection. Sparse-file validation depends on filesystem support and can produce warnings for zero-filled data blocks where stats expected holes. `SetPageLoadedStatus` can grow the logical file by marking beyond the current size. Multipart planning must preserve minimum-part constraints and avoid generating invalid final parts.

Test signals: `src/test_page_list.cpp` directly tests compression, loading status, and unloaded-page discovery. Integration tests for skipped writes, non-boundary writes, mixed multipart, cache stat deletion/reload, and cache checking are the main behavioral coverage.
