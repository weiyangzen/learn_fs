# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsclstate.h

This header defines the in-memory NFSv4/NFSv4.1 client state graph.

Key contents:
- Defines list heads for clients, owners, opens, lock owners, byte locks, delegations, layouts, file layouts, device info, and layout recalls.
- Defines delegation and layout hash sizes and hash macros.
- `struct nfsclsession` stores NFSv4.1 session state, callback slots, slot sequence numbers, slot bitmap, limits, and session id.
- `struct nfsclds` stores MDS/DS session and socket information for pNFS.
- `struct nfsclclient` is the root client state object, holding owners, delegations, layout/device collections, renewal thread, mount pointer, lease/recovery flags, callback id, and variable-length client id.
- `struct nfsclowner`, `struct nfsclopen`, `struct nfscllockowner`, and `struct nfscllock` model open owners, opens, lock owners, and byte ranges.
- `struct nfscldeleg` stores delegation stateid, delegation-local owners/locks, credential, file handle, flags, size/change cache, and local modify time.
- pNFS structures include `nfscllayout`, `nfsclflayout`, `nfsclrecalllayout`, and `nfscldevinfo`.
- Inline helpers index variable-layout device info arrays for data-server addresses and stripe indices.
- `NFSCL_INCRSEQID()` conditionally increments seqids based on request flags.

Important dependencies:
- Used by client state and RPC code declared in `nfs_var.h`.
- Uses shared `nfsv4lock` and NFSv4 stateid types.

Risks and notes:
- Many structures are variable-length with trailing arrays; allocation and bounds are critical.
- Session slot state and pNFS layout/device references require strict locking/refcount discipline in implementation files.
