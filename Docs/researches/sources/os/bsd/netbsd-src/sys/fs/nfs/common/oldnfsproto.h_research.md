# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/oldnfsproto.h

This legacy protocol header preserves older NFSv2/v3 and early NFSv4 definitions from the pre-newnfs import path. It overlaps heavily with `nfsproto.h` but uses older names, smaller maximum data assumptions, older error naming, older NFSv4 operation spellings, and additional legacy structs such as `union nfsfh` and `struct nfsv4_fattr`.

Key contents:
- Defines NFS port/program/version constants, v2/v3 maximum data and packet sizes, path/name limits, and traditional NFS status values.
- Defines older fake/internal status marker bits such as `NFSERR_RETVOID`, `NFSERR_AUTHERR`, and `NFSERR_RETERR`.
- Defines wire sizes for v2/v3 file handles, attributes, writable attributes, cookies, write verifiers, create verifiers, statfs, fsinfo, pathconf, and basic v4 verifier/file-handle/stateid sizes.
- Defines generic NFS procedure numbers, actual NFSv2 procedures, NFSv4 COMPOUND procedure number, and NFSv4 operation numbers through WRITE using older names such as `NFSV4OP_OPEN_CONFIRM`.
- Defines v3 access/write/create/fsinfo constants and v4 access/open-share constants.
- Defines file type enum `nfstype`, NFSv4 claim/stability/open/create/time/delegation enums, `union nfsfh`, v2/v3 time structs, 64-bit protocol quad helpers, NFSv3 special device struct, and NFSv4 bitmap/changeinfo structs.
- Defines v2/v3 file attribute and set-attribute structs, `struct nfsv4_fattr` with valid-field bits, old NFSv4 attribute-number macros, bitmap manipulation macros, statfs, fsinfo, and pathconf structures.

Important behavior:
- This header is not identical to `nfsproto.h`. The newer header has broader NFSv4.1/pNFS coverage and modernized names, while this one preserves old ABI/source expectations.
- `NFS_SMALLFH` defaults to 128 here, and `union nfsfh` stores small file handles directly.
- The older NFSv4 bitmap handling only uses two 32-bit words (`FA4_ZERO` zeros 8 bytes), unlike the newer three-word bitmap model in `nfsproto.h`.

Research notes:
- Treat this as compatibility material for old code, not as the authoritative new NFS protocol header.
- Risk areas are accidental inclusion alongside `nfsproto.h`, conflicting macro names, and stale NFSv4 definitions that do not include v4.1 behavior.
