# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsproto.h

`nfsproto.h` is the protocol constants and wire-format definition header for NFSv2, NFSv3, NFSv4.0, NFSv4.1, NFSv4.2, pNFS, ACLs, extended attributes, and related RPC sizing.

Key contents:
- Defines core NFS identity and limits: `NFS_PORT`, `NFS_PROG`, callback program, versions, max path/name/data sizes, packet/XDR overhead, server max I/O defaults, and minor versions.
- Defines NFS protocol error values, including stable RFC-defined values, NFSv4.1/v4.2 additions, extended attribute errors, internal synthetic errors (`NFSERR_STALEWRITEVERF`, `NFSERR_DONTREPLY`, etc.), and RPC/authentication-tagged error values.
- Defines XDR sizes for handles, attributes, statfs/fsinfo/pathconf structures, stateids, GSS headers, device ids, file layouts, and flex-file layouts.
- Defines NFS procedure numbering across v2/v3/v4 plus synthetic client procedure identifiers for v4.1/v4.2, pNFS, extended attributes, append write, openattr, clone, and related operations.
- Defines NFSv2 actual RPC procedure numbers and NFSv4 compound/callback procedure numbers.
- Defines NFSv4 constants for locking, open claims, delegation return values, share access/deny, open result flags, file-handle volatility, access bits, write stability, create modes, exchange-id flags, sessions, sequence flags, pNFS layout types, device notifications, and callback recall-any bits.
- Under kernel builds, defines vnode-to-NFS conversion macros, `nfstype`, NFS time structs, packed 64-bit protocol representation, NFSv2/v3 attribute structs, NFSv2/v3 set-attribute structs, and NFSv4.2 IO advise hint bits.
- Defines extensive NFSv4 attribute bit numbers and masks, including supportable, settable, gettable, statfs/pathconf/readdirplus/referral groups, v4.1-only and v4.2-only attributes, POSIX draft ACL attributes, xattr support, clone block size, and change attribute type.
- Defines operation bitmaps and SP4_MACH_CRED must/allowed operation filtering macros.
- Defines in-memory helper structs for statfs, fsinfo, pathconf, NFSv4 stateids, notification bitmaps, seek contents, extended-attribute set modes, POSIX draft ACL models/scopes/tags/permissions, and change attribute types.

Important integration points:
- The error values below `10000` intentionally mirror FreeBSD `errno` values; the comments warn that changing `errno` mappings would require NFS translation changes.
- Attribute bitmap definitions are central to NFSv4 compound construction and server/client advertised capability handling.
- Wire structs avoid native 64-bit fields where alignment would make direct XDR copying unsafe.
- Procedure and operation counts drive statistics array sizing and DTrace probe arrays elsewhere in this group.

Research notes:
- This file is the primary protocol vocabulary for the FreeBSD NFS stack.
- It combines RFC-fixed values with FreeBSD-internal synthetic values; consumers must distinguish values that go on the wire from local control/status values.
