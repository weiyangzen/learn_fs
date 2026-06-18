# sources/user-network-fs/s3fs-fuse/src/fdcache_entity.h

Purpose: Declares `FdEntity`, the per-open-object abstraction for cached reads, writes, uploads, metadata changes, page-list state, and pseudo-fd management.

Important APIs and types: Defines `fdinfo_map_t` and `fdent_map_t`. `FdEntity` is `enable_shared_from_this` and non-copyable/non-movable. Public methods cover open/close, pseudo-fd lookup/duplication, path rename, stats and metadata access, timestamp/mode/owner/xattr/content-type mutation, load/read/write/flush, hole punching, dirty marking, and untreated-part manipulation. Private `pending_status_t` represents metadata and create-file pending work.

Control flow contract: `FdManager` owns shared instances and calls `Open`/`Close`; FUSE-facing code usually reaches methods through `AutoFdEntity`. Callers must pass pseudo-fds obtained from this entity. Lock annotations document which helpers require `fdent_lock` and/or `fdent_data_lock`.

State and persistence behavior: Header documents the split between logical path/physical fd/upload info and data/cache/page metadata. `PageList` plus `CacheFileStat` persist loaded/modified ranges by cache inode. `orgmeta`, `timestamps`, and `pending_status` determine whether flush performs data upload, metadata copy update, or new-file creation.

Dependencies and integration points: Includes `fdcache_page.h`, `fdcache_untreated.h`, `metaheader.h`, `s3fs_util.h`, and `filetimes.h`; forward-declares `PseudoFdInfo`. Used by `FdManager`, `PseudoFdInfo`, `AutoFdEntity`, and FUSE operations.

Risks: The class exposes a broad surface with raw pseudo-fd integers and manual lock discipline. `friend class FdEntity` access to `PageList` internals and `get_shared_ptr` use during manager remap make ownership assumptions important. Header-level lock annotations are only as strong as tooling support.

Test signals: Compile-time coverage comes from the main build. Runtime coverage should include open/reopen, truncate, sparse writes, metadata-only updates, multipart modes, stream upload, no-cache fallback, and rename while open.
