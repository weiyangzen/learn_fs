# sources/user-network-fs/libnfs/lib/libnfs.c

## Purpose

`libnfs.c` is the main high-level asynchronous libnfs client layer. It owns context initialization and destruction, URL parsing, directory cache management, connection setup through portmapper or explicit ports, TLS and Kerberos connection negotiation, public async API dispatch to NFSv3 or NFSv4 backends, read chunking, readonly enforcement, path normalization, configuration setters, error storage, mount export async helpers, and RPC null tasks. The synchronous API in `libnfs-sync.c` wraps the functions defined here.

## Important APIs, Types, and Functions

Lifecycle and state APIs include `nfs_init_context`, `nfs_destroy_context`, `nfs_get_rpc_context`, `nfs_get_server_address`, `nfs_get_server`, `nfs_get_export`, `nfs_get_rootfh`, `nfs_get_fh`, `nfs_umask`, `nfs_set_error`, and `nfs_set_error_locked`. Directory ownership is handled by `nfs_free_nfsdir`, `nfs_dircache_add`, `nfs_dircache_find`, `nfs_dircache_drop`, `nfs_readdir`, `nfs_telldir`, `nfs_seekdir`, `nfs_rewinddir`, and `nfs_closedir`.

URL handling is centered on `nfs_parse_url`, exposed as `nfs_parse_url_full`, `nfs_parse_url_dir`, `nfs_parse_url_incomplete`, and released with `nfs_destroy_url`. URL query parameters are applied through `nfs_set_context_args` and `nfs_set_context_args_no_val`, covering options such as `uid`, `gid`, `timeo`, `retrans`, `debug`, `auto-traverse-mounts`, `dircache`, `autoreconnect`, `version`, `nfsport`, `mountport`, `rsize`, `wsize`, `readdir-buffer`, optional interface binding, TLS `xprtsec`, and Kerberos `sec`.

Connection APIs are `rpc_connect_port_async`, `rpc_connect_program_async`, and callback stages `rpc_connect_program_1_cb` through `rpc_connect_program_6_cb`. They connect first to portmapper when needed, resolve a program port for IPv4 or IPv6, reconnect to the target program, issue a NULL RPC, optionally negotiate RPC-with-TLS using `rpc_null_task_authtls`, and optionally initialize RPCSEC_GSS with `rpc_null_task_gss`.

Public async NFS operations include mount and unmount, stat/lstat/fstat variants, open/open2, chdir, pread/read/preadv/readv, pwrite/write, close, fsync, ftruncate/truncate, mkdir/rmdir/creat/mknod/unlink, opendir, lseek, NFSv4 lockf/fcntl, statvfs/statvfs64, readlink, chmod/lchmod/fchmod, chown/lchown/fchown, utimes/lutimes/utime, access/access2, symlink, rename, and link. Configuration getters/setters include read/write max, uid/gid/auxiliary groups, debug, auto traversal, readonly, dircache, autoreconnect, retrans, version, ports, readdir buffer sizes, poll timeout, timeout, stats/log callbacks, and PDU stats.

## Control Flow

Context initialization allocates `struct nfs_context_internal`, `struct nfs_context`, and an RPC context, sets defaults, initializes optional Kerberos username, sets cwd to `/`, enables auto traversal and directory cache, configures hard-mount-like resiliency defaults, selects NFSv3 as the default version, sets transfer sizes and readdir buffers, seeds NFSv4 verifier and client name, initializes multithreading locks, and ignores SIGPIPE on supported non-Windows platforms. Destruction walks nested mounts and directory cache lists, destroys the RPC context, frees error strings and NFS state, destroys multithreading locks, and releases per-thread contexts.

URL parsing validates the `nfs://` prefix, percent-decodes the server/path string, parses optional server port, splits server/path/file depending on full versus directory mode, applies query options, handles `username@server`, records the selected port, and performs TLS global initialization if `xprtsec=tls` or `xprtsec=mtls` was requested. Path normalization mutates absolute paths in place by collapsing `//`, `/./`, and parent-directory segments while rejecting paths that escape above root.

Most async public functions are dispatchers. They inspect `nfs->nfsi->version` and call the matching `nfs3_*` or `nfs4_*` backend, returning an error for unsupported version/operation combinations. Mutating operations check `nfsi->readonly` and usually complete through the callback with `-EROFS` without starting a backend RPC. File-handle writes and truncates also reject `nfsfh->is_readonly`.

Read chunking uses `struct rw_data`. `_nfs_pread_async` sends a single backend read when the request is smaller than `nfs_get_readmax`; larger requests allocate a continuation object, submit the first chunk, and `r_cb` advances buffer, offset, and remaining count until all bytes are read or a short read indicates EOF. `nfs_read_async` uses `nfsfh->offset` and requests offset updates, while `nfs_pread_async` leaves file position unchanged. Vectored reads dispatch directly to v3/v4 internal preadv helpers.

## State and Persistence Behavior

The durable in-process state is `struct nfs_context` plus `struct nfs_context_internal` and the shared `struct rpc_context`. `nfsi` stores cwd, root file handle, server/export strings, nested mounts, directory cache, NFS version/default-version state, transfer sizes, readonly and cache flags, resiliency defaults, NFSv4 verifier/client name, ports, and optional thread contexts. Directory handles are cached on close when directory caching is enabled and evicted after `MAX_DIR_CACHE` entries. Error strings are heap allocated per context, with special handling for a static out-of-memory string.

No filesystem persistence is performed. Network session persistence is delegated to the RPC context, including connection state, queues, timeouts, auth state, TLS state, and reconnect behavior. Several setters store user choices in `nfsi` until mount completion, when lower layers can apply them to the RPC transport.

## Dependencies and Integration Points

`libnfs.c` is the integration hub for `libnfs.h`, `libnfs-private.h`, raw generated mount/portmap/NFS protocol headers, `nfs_v3.c`, `nfs_v4.c`, RPC socket/PDU/init code, TLS helpers when `HAVE_TLS` is enabled, Kerberos wrapper code when `HAVE_LIBKRB5` is enabled, and multithreading wrappers when `HAVE_MULTITHREADING` is enabled. Its public async functions are the immediate dependency of the synchronous wrappers. The URL parser also integrates with platform-specific interface binding when `HAVE_SO_BINDTODEVICE` is available.

## Risks and Edge Cases

The file has a broad API surface and many feature gates, so regressions often appear as mismatched v3/v4 behavior, missing callback completion, or inconsistent errno conventions. URL parsing is pointer-mutating and has delicate cases around percent-decoding, `server:port`, incomplete URLs, query options, `username@server`, and file-versus-directory splitting. Transfer-size setters clamp and round to 4096-byte units; very small user values are raised to minimums, which can surprise callers. `nfs_set_error` allocates a fixed 1024-byte message and must be used carefully with multithreaded contexts to avoid losing thread-local errors.

Connection setup spans portmapper, target reconnect, NULL RPC validation, TLS negotiation, and optional Kerberos initialization; each stage owns callback data and must free it exactly once. `rpc_null_task` and related functions must free PDUs on queue failure or they risk leaks. Read chunking must handle `readmax == 0`, short reads, callback errors, and offset updates correctly. Directory caching returns an owned cached directory from `nfs_dircache_find`; callers must not double-free cached handles. Several async functions synchronously invoke callbacks for readonly errors, so wrapper code must be reentrant-safe.

## Test Signals

Strong signals are end-to-end async and sync tests for both NFSv3 and NFSv4, including mount/unmount, path resolution, file creation/open/read/write/close, metadata, directory listing and cache reuse, chmod/chown/time changes, link/rename/symlink, statvfs, and NFSv4 lock/fcntl paths. URL parser tests should cover percent escapes, invalid ports, incomplete URLs, query options, TLS/Kerberos options, username extraction, and directory/file modes. Fault tests should cover allocation failures in context and connection callback data, portmapper program-not-found, IPv6 getaddr parsing, TLS handshake rejection, Kerberos init failure, readonly callbacks, transfer-size clamping, read chunking over multiple chunks, and context destruction with cached directories and thread contexts. Build matrix signals should include plain, TLS, Kerberos, Windows, pthread, and no-multithreading configurations.
