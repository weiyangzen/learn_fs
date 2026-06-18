# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvstate.h

`nfsrvstate.h` defines NFSv4 server-side state structures: clients, sessions, opens, locks, delegations, layouts, local lock rollback, user/group caches, pNFS device metadata, and pNFS data-server file records.

Key contents:
- Declares list/head types for clients, states, locks, lock files, sessions, layouts, DS directories, devices, dont-list markers, and user/group cache buckets.
- Defines hash macros for clientid, stateid, uid/gid, user/group names, sessions, and layouts.
- Defines `struct nfsclient`, the server representation of an NFSv4 client, including stateid hash table, open/delegation/session lists, lease/expiry data, clientid/confirm verifiers, SP4_MACH_CRED operation bitmaps, callback info, uid/gid, client strings, callback socket request data, and flags.
- Defines `struct nfslayout`, representing pNFS layout state with stateid, clientid, file handle, device id, fsid, layout length/type/flags/mirror count, and variable XDR payload.
- Defines `struct nfsdsession`, the NFSv4.1 session object with slot table, associated client, limits, callback parameters, session id, and callback session. Comments document locking order and field-level lock responsibilities.
- Defines overloaded `struct nfsstate`, used for open owners, open files, lock owners, lock state, and delegations. It contains list/hash links, stateid, sequence, uid, flags, owner bytes, associated lock file/cache/client pointers, and union fields for open/delegation-specific metadata.
- Defines `struct nfslock`, `struct nfslockconflict`, and `struct nfsrollback` for byte-range lock state, conflict reporting, and local lock rollback.
- Defines `struct nfslockfile`, grouping opens, delegations, locks, local locks, rollback entries, file handle, local-lock serialization, and use count per file.
- Defines `struct nfsusrgrp`, a name/id/credential cache entry with numeric and name hash links plus expiry/wired state.
- Defines stable restart record header `struct nfsf_rec` and prototypes for client/delegation cleanup.
- Defines `struct nfsdevice` for pNFS data-server device info, including DS directory vnodes, host/address strings, device id, MDS fsid/stripe size, and no-space state.
- Defines old/new pNFS DS attribute records (`opnfsdsattr`, `pnfsdsattr`) and recovery dont-list entries.
- Defines pNFS DS file xattr records (`opnfsdsfile`, `pnfsdsfile`) outside the kernel-only block so on-disk/xattr layout can be shared.

Important integration points:
- This is a server state ABI/layout header internal to kernel NFS code, not just declarations.
- Locking comments on `struct nfsdsession` are critical: state lock and session-hash lock ordering prevents races during session lookup/add/delete.
- Several structs use trailing flexible/one-byte arrays and are malloced to exact size.
- pNFS metadata xattr structs encode persistent data-server layout state and must remain compatible with existing metadata.

Research notes:
- The file is foundational for NFSv4 correctness: lease recovery, stateid lookup, open/lock/delegation lifecycle, sessions, and pNFS layout/device state all depend on these layouts.
