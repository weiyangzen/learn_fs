# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsnode.h

## Purpose
Defines `struct nfsnode`, the NFS client equivalent of an inode attached to each active vnode, plus structures for sillyrename, directory cookie maps, access-cache entries, flag bits, conversion macros, and client vnode helper prototypes.

## Main Data
- `struct sillyrename` stores deferred unlink state: task, credential, parent directory vnode, generated `.nfs...` name, and name length.
- `struct nfsdmap` maps logical directory offsets to NFS cookies in chunks of `NFSNUMCOOKIES`, with v3 and v4 cookie storage variants.
- `struct nfs_accesscache` caches an `ACCESS` result mode for one UID with a timestamp.
- `struct nfsnode` stores mutex-protected vnode state: file size, modification revisions, cached attributes, attr-cache timestamp, access cache, previous modify time, file handle pointer, vnode/parent pointers, lockf pointer, saved write error, special-file timestamps or directory cookie verifier, directory EOF or mtime, sillyrename pointer or cookie list, direct I/O count, NFSv4 change attribute, NFSv4 name metadata, write credential, cached open stateid, and last local modification time.

## Flags
Important `n_flag` bits cover directory cookie serialization, modified buffers, delayed write errors, create/truncate markers, size/cache invalidation, non-cacheable direct I/O, special-file access/update/change, delegation modification/recall, remove-in-progress waiters, node sleep lock, pNFS layout denial, write-open tracking, lock history, DS commit requirement, possible lock state, and openattr unsupported state.

## Interfaces
- `VTONFS(vp)` and `NFSTOV(np)` convert between vnode and nfsnode.
- `NFS_TIMESPEC_COMPARE()` compares timestamps.
- Kernel prototypes cover page I/O, write, inactive/reclaim, sillyrename removal, node lookup/creation, directory cookie mapping, directory invalidation, vnode lock upgrade helpers, and directory cookie lock/unlock.

## Integration
Used directly by `nfs_clvnops.c` for nearly every vnode operation and by node-cache, bio/page, NFSv4 state, pNFS, and directory-cookie code elsewhere in the client.

## Risks
- Several unions reuse the same storage for special-file timestamps, directory cookie verifier, directory EOF offset, sillyrename pointer, and cookie lists; callers must respect vnode type.
- Most fields are protected by `n_mtx`; missed locking can corrupt file size, cached attributes, flags, direct I/O counters, access cache, cookie state, and delayed write errors.
- `n_localmodtime` is a coherency guard against stale RPC attributes racing local size changes; bypassing it can install older size/mtime data.
