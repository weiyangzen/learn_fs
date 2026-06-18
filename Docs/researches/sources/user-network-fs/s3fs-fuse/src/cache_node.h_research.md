<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache_node.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/cache_node.h

Purpose: declares the stat-cache tree abstraction used by s3fs to represent cached S3 object metadata and directory hierarchy. It defines base and derived node types, expiration control, negative-cache support, counters, locking annotations, and an RAII guard for temporarily preventing expiration checks.

Important APIs/types: `StatCacheNode` is the base class and `enable_shared_from_this` owner for cached objects. `FileStatCache`, `DirStatCache`, `SymlinkStatCache`, and `NegativeStatCache` specialize object behavior. `statcache_map_t` maps child leaf names to node pointers. `stat_counter_pos` maps `objtype_t` categories to counter slots. `PreventStatCacheExpire` calls `StatCacheNode::PreventExpireCheck` in its constructor and `ResumeExpireCheck` in its destructor.

Control flow surface: public methods wrap protected `HasLock` methods with the global cache mutex. External callers add stat/meta data with `Add`, store cached listings with `AddS3ObjList`, query nodes with `Find`/`Get`, get symlink extra values with `GetExtra`, enumerate children with `GetChildMap`, and force invalidation with `RemoveChild`/`TruncateCache`. Directory overrides perform recursive path routing and maintain child/list state; negative nodes override ETag and expiration semantics.

State and persistence: declares static cache-wide state for counters, expiration settings, negative-cache setting, the global mutex, and expiration-suppression bookkeeping. Base nodes store full path, type, hit count, cache timestamp, no-truncate flag, stat buffer, filtered metadata, and optional extra value. Directory nodes store an independent mutex, last truncate-check time, destructor-time type backup, children, and optional `S3ObjList`. Everything is in-memory and rebuilt from S3 or filesystem actions.

Dependencies/integration: includes `common.h` for thread-safety annotation macros and global types, `metaheader.h` for `headers_t`, `s3objlist.h` for directory listing cache, and `types.h` for `objtype_t`/object-type macros. The annotations are intended for clang thread-safety analysis and document lock requirements across implementation methods.

Risks: the class exposes many overloaded operations with subtly different semantics, especially `Update` versus `Set`, directory `ClearData`, and extra-value handling only for symlinks. Lock annotations help, but one static mutex for all base state makes future fine-grained changes easy to get wrong. The friend relationship grants `DirStatCache` access to protected members for recursive maintenance, increasing coupling. Directory path invariants require trailing slashes and child keys without slashes; callers must pass normalized full paths or rely on constructor/add logic.

Test signals: compile-time thread-safety checks under clang are valuable for this header. Behavioral tests should instantiate each node class, verify counter movement through construction/destruction/type update, ensure public wrappers acquire locks and delegate correctly, validate path suffix invariants, and check RAII expiration suppression nests and resumes properly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache_node.h -->
