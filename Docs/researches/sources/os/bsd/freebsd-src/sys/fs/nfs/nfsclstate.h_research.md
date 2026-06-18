# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsclstate.h

This header defines the NFSv4 client-side state model: client IDs, open owners, opens, lock owners, byte-range locks, delegations, NFSv4.1 sessions, data-server connections, pNFS layouts, flex-file mirrors, recall records, and device information.

Key behavior:
- Declares list/head types and hash macros for delegations, opens, layouts, lock owners, and device info.
- `struct nfsclsession` stores NFSv4.1 session state: mutex, callback slots, client id, backchannel transport, slot sequence numbers, active/bad slot bitmaps, limits, slot counts, session id, and defunct status.
- `struct nfsclds` represents an MDS/DS server endpoint with session state, socket request pointer, expiry, verifier, flags, and variable-length server owner.
- `struct nfsclclient` stores a mounted client’s NFSv4 state roots: owner/open/delegation/layout/device lists and hashes, shared lock, renew thread, mount pointer, expiry, counters, clientid revision, callbacks, flags, and variable client id.
- `struct nfsclowner` tracks an open-owner sequence stream and its opens.
- `struct nfscldeleg` tracks a delegation for a file handle, including delegated stateid, ACE, local owners/locks, credential, size/change/modtime snapshots, timestamps, and flags.
- `struct nfsclopen` tracks an open stateid, owner, credential, mode, open count, POSIX locking state, and file handle.
- `struct nfscllockowner` and `struct nfscllock` track NFSv4 byte-range lock ownership and local lock ranges.
- `struct nfscllayout`, `struct nfsclflayout`, `struct nfsffm`, `struct nfsclrecalllayout`, and `struct nfscldevinfo` define pNFS file/flex-file layout segments, mirrors, recalls, and device-address mappings.
- Inline helpers return device address slots and get/set compact stripe indices stored after the device-address pointer array.
- Defines state flag sets for data-server endpoints, clients, delegations, layouts, file-layout segments, and device info.
- Defines `NFSCL_INCRSEQID()` to increment an owner seqid only when the descriptor indicates it should.

Important interactions:
- The structs are consumed by `nfs_clstate.c`, `nfs_clrpcops.c`, session sequencing in `nfs_commonsubs.c`, and pNFS I/O/layout code.
- Hash macros depend on `ncl_hash()` and file-handle bytes to locate open/delegation/layout records.
- Layout/device structures share variable-length trailing storage; allocation size must match file-handle, address, stripe-index, or mirror counts exactly.

Edge cases:
- `nfsclsession` slot state uses 64-bit slot bitmaps and a fixed 64-entry sequence array, so session slot counts are bounded by that representation.
- Defunct sessions, bad slots, recalled layouts, returned layouts, and forced unmount flags are represented explicitly and must be checked by session/layout users.
- Flex-file and file-layout variants share unions; code must consult flags before interpreting the union fields.
