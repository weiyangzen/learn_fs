# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsproto.h

This header defines the main NFS protocol vocabulary for the new NetBSD NFS stack. It covers NFSv2, NFSv3, NFSv4.0, NFSv4.1, and preparatory NFSv4.2 constants: port/program/version numbers, NFS status codes, wire sizes, procedure numbers, NFSv4 operation constants, access/open/share/ACL flags, attribute bitmaps, pNFS layout flags, type conversion macros, and protocol data structures.

Key contents:
- Defines core constants: `NFS_PORT`, `NFS_PROG`, `NFS_CALLBCKPROG`, protocol versions, maximum path/name sizes, server maximum I/O (`NFS_SRVMAXIO`), packet sizes, and NFSv4 minor/callback versions.
- Lists NFS error/status values from traditional errno-compatible values through NFSv3/v4 extended values, NFSv4.1 session/pNFS errors, fake internal NFS errors, and RPC/auth error marker bits.
- Defines protocol wire sizes for unsigned values, hyper values, NFSv2/v3/v4 file handles, attributes, wcc data, fsinfo, pathconf, stateids, GSS headers, session IDs, and device IDs.
- Defines generic NFS procedure numbers, actual NFSv2 procedure numbers, and NFSv4 COMPOUND/callback procedure numbers.
- Provides NFSv4 open, lock, delegation, share-deny, create, access, fsinfo, ExchangeID, CreateSession, Sequence, LayoutReturn, layout type, I/O mode, device-info, and file-layout utility flags.
- Provides NFSv4 ACE type, supported-type, inherit, and access mask constants plus mappings from mode-like read/write/execute concepts to ACE masks.
- Defines vnode/NFS type conversion macros and file type enum `nfstype`.
- Defines dense wire-facing structs for NFSv2/v3/v4 times, 64-bit protocol quads, NFSv3 special device numbers, v2/v3 file attributes, v2/v3 settable attributes, statfs, fsinfo, pathconf, and NFSv4 stateids.
- Defines NFSv4 attribute bit numbers and 32-bit bitmap masks across three bitmap words, including supported, settable, getattr, write-getattr, wcc, callback-getattr, statfs, pathconf, readdirplus, and referral attribute sets.

Important behavior:
- Many status values below 10000 intentionally match `sys/errno.h`; the file comments warn that if errno values change, explicit mapping would be required.
- Wire structs avoid native 64-bit integer fields where alignment could differ from XDR layout. The code uses arrays of 32-bit words and conversion helpers instead.
- The NFSv4 bitmap constants are positional: names such as `NFSATTRBM_MODE` repeat bit values in different bitmap words, so callers must combine them with the correct word context.
- `NFSATTRBIT_WRITEGETATTR*` deliberately excludes owner and owner-group relative to normal getattr sets, matching client write-path avoidance of name-mapping upcalls.
- pNFS-related constants (`NFSLAYOUT_NFSV4_1_FILES`, `NFSFLAYUTIL_DENSE`, `NFSFLAYUTIL_COMMIT_THRU_MDS`) are consumed by NFSv4.1 layout/device paths.

Research notes:
- This is the authoritative protocol constant header for new NFS. Any operation decoder, XDR marshaller, stats table, or NFSv4 attribute parser should be checked against it.
- High-risk changes include attribute bitmap edits, status-code mappings, packed struct assumptions, and procedure/operation numbering shared with stats and generated RPC logic.
