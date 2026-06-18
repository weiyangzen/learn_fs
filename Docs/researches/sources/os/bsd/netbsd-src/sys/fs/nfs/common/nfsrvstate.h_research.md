# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvstate.h

This header defines the NFSv4 server-side state model: clients, sessions, open owners, opens, lock owners, byte-range locks, delegations, local lock rollback records, per-file state containers, user/group name cache entries, and stable-storage restart records.

Key contents:
- List-head definitions for client hashes, state lists, lock lists, lockfile hashes, session lists, session hashes, and user/group name hashes.
- Hash macros for clients, stateids, user IDs/names, group IDs/names, and sessions.
- `struct nfsclient`, representing an NFSv4 client ID with hash/list linkage, stateid hash table, open/delegation/session lists, expiry and delegation times, client/confirm IDs, callback program/id, state index counters, callback refcount, credential identity, name/principal lengths, callback socket request, flags, verifier, and variable client ID bytes.
- `struct nfsdsession`, representing an NFSv4.1 session with refcount, hash/list links, slot table, associated client, creation flags, fore/back channel limits, session ID, and callback session state.
- `struct nfsstate`, a deliberately overloaded state object used for open owners, open files, lock owners, and delegated files. It carries stateid, sequence, uid, flags, owner data, list/hash/file links, owner/open/delegation-specific union state, back-pointers, and optional operation-cache reference.
- `struct nfslock`, representing byte-range locks linked both by owner and file.
- `struct nfslockconflict`, the returned conflict descriptor with clientid, range, flags, owner length, and owner bytes.
- `struct nfsrollback`, used to track local locks that may need rollback.
- `struct nfslockfile`, the per-file container for opens, delegations, locks, local locks, rollback entries, file handle, local-lock serializer, and usecount.
- `struct nfsusrgrp`, a cached user/group name-to-id entry with hash links, expiry, id, credential, and variable-length name.
- `struct nfsf_rec`, the stable restart file header containing lease duration and number of boot times.
- Kernel prototypes for `nfsrv_cleanclient()` and `nfsrv_freedeleglist()`.

Important behavior:
- The comments specify strict locking rules for `struct nfsdsession`: list modification needs global state lock then session-hash lock; traversal needs one of those locks; refcount manipulation needs global state lock; callback-session fields require the callback session mutex.
- `struct nfsstate` multiplexes several state roles, so its union fields are valid only in specific contexts. Misinterpreting `ls_un` or list membership can corrupt state recovery.
- File locking state is indexed both by owner and by file, enabling conflict detection, cleanup by client, cleanup by file handle, and stateid lookup.
- Stable-storage records in this header tie into NFSv4 grace/reclaim behavior and crash recovery.

Research notes:
- This file is essential for understanding `nfs_nfsdstate.c`, delegation recall, lock conflict handling, reclaim, and NFSv4.1 session cleanup.
- Review risk centers on lock ordering, overloaded state object invariants, stateid hashing, reference counts, and variable-length allocation boundaries.
