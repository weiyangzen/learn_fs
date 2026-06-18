# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_subr.c

NFSv4 client support routines for shared protocol helpers, RPC handle caching, compound RPC dispatch, volatile-filehandle remapping, readdir caching, zone-local client state, direct I/O toggling, and failover classification.

Key responsibilities:
- Provides basic NFSv4 object helpers: filehandle copy/compare, stateid compare, errno/NFSv4 status translation, NFSv4 time conversion, UTF-8/string conversion, directory-name validation, and bad-owner diagnostics.
- Manages per-zone RPC client-handle caches through `clget4()`, `clfree4()`, `clreclaim4_zone()`, zone init/fini hooks, and the global low-memory reclaim callback.
- Implements `authget()` security-handle selection, including server-provided SECINFO retry state via `SV4_TRYSECINFO`.
- Implements the central client RPC path: `nfs4_rfscall()` performs RPC handle acquisition, signal masking, hard/soft mount retry behavior, timeout backoff, failover return decisions, zone-shutdown/forced-unmount exits, and recovery fact/event queueing. `rfs4call()` wraps this for NFSv4 `COMPOUND` calls and updates per-operation stats.
- Supports failover and volatile filehandle recovery with `remap_lookup()`, `nfs4_remap_file()`, `nfs4_check_remap()`, and `nfs4_make_dotdot()`, rebuilding filehandles from stored path state and updating attributes, parent handles, stubs, and shared filehandle records.
- Frees server information chains with `sv4_free()` and prints/debugs filehandles and rnodes under DEBUG.
- Implements an AVL-backed NFSv4 readdir response cache keyed by cookie and request count, with reference counting, wait/broadcast behavior while entries are being filled, purge, destroy, and interrupt handling.
- Initializes and tears down NFSv4 subr state with `nfs4_subr_init()` and `nfs4_subr_fini()`, including the client-handle cache and zone key.
- Implements `nfs4_directio()` and `nfs4_has_pages()` for page-cache flushing/direct I/O state.
- Classifies failover-worthy RPC errors through `nfs4_try_failover()` and the indexed `try_failover_table`.
- Provides `nfs4_error_zinit()` and `nfs4_error_init()` convenience initializers.

Major dependencies:
- Kernel primitives: zones, kmem caches, kstats, AVL trees, mutexes, condition variables, credentials, signals, vnode/VFS, and DTrace/SDT probes.
- RPC/TLI client APIs: `CLIENT`, `CLNT_CALL`, `clnt_tli_kcreate`, `clnt_tli_kinit`, auth handles, and RPC status/error structures.
- NFSv4 client internals from `nfs4.h`, `rnode4.h`, and `nfs4_clnt.h`, including `mntinfo4_t`, `servinfo4_t`, `rnode4_t`, recovery state, shared filehandles, filename/path helpers, compound XDR helpers, recovery queues, and attribute cache functions.

Important control flow:
- Normal over-the-wire calls go through `rfs4call()` -> `nfs4_rfscall()` -> `nfs_clget4()`/`clget4()` -> `authget()` -> `CLNT_CALL()` -> `clfree4()`.
- Hard mounts keep retrying retryable RPC failures with exponential backoff unless shutdown, forced unmount, interrupt, unrecoverable RPC status, or failover handling takes over.
- Failover mounts return selected transport errors to higher recovery code instead of looping locally.
- Remap recovery uses the mount root and the rnode’s saved path to issue lookup compounds, then validates type/size where requested before replacing the rnode’s filehandle and cached attributes.
- Readdir cache lookup may drop locks for sleeping allocation and re-search afterward; callers must hold the rnode read lock and state lock on entry.

Concurrency and locking:
- Client-handle cache state is protected by `nfscl_chtable4_lock`.
- Global per-zone client data is protected by `nfs4_clnt_list_lock`.
- Readdir cache trees are protected by the rnode state lock, while individual cache entry refcounts have their own mutex.
- Remap and recovery paths coordinate with mount recovery locks, rnode state locks, and shared filehandle update helpers.
- Several paths deliberately avoid holding locks across sleeping allocation or RPC.

Notable risks:
- `str_to_utf8()` sets zero-length state for null/empty input but does not return before `strlen(nm)`, so callers must not pass null despite the apparent guard.
- The UTF-8 conversion routines mostly validate embedded nulls and slash/name restrictions; they do not perform full RFC UTF-8 validation.
- `nfs4_rfscall()` has many mount-state exits; changes can easily affect forced unmount, zone shutdown, recovery-thread behavior, or hard-mount retry semantics.
- Readdir cache correctness depends on precise lock ordering around `r_rwlock`, `r_statelock`, entry condition variables, and purge/removal flags.
- Filehandle remap updates must preserve vnode type/size expectations or intentionally mark recovery failed; otherwise stale or crossed-server objects could be misrepresented.
- The failover table assumes RPC enum values are stable enough for direct indexing, with fallback behavior if they are not.
