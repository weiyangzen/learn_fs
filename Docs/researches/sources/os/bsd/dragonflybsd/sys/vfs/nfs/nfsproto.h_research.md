# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsproto.h

## Purpose

`nfsproto.h` defines wire-level NFSv2/NFSv3 constants, procedure numbers, error codes, XDR field sizes, type conversion macros, file handle representation, and packed protocol structures.

## Main Contents

- Protocol constants:
  - NFS port/program/version IDs,
  - max transfer/path/name/header/packet sizes,
  - NFS block accounting size.
- Error constants:
  - standard v2/v3 NFS errors,
  - v3-only extended errors,
  - DragonFly-internal markers such as `NFSERR_RETVOID`, `NFSERR_AUTHERR`, `NFSERR_RETERR`, and fake `NFSERR_STALEWRITEVERF`.
- XDR size constants for v2/v3 file handles, attributes, setattr, cookies, statfs, fsinfo, pathconf, WCC, write verifier, and create verifier.
- Generic NFS procedure numbers and mapped actual NFSv2 procedure numbers.
- NFSv3 operation constants:
  - setattr time modes,
  - access bitmask values,
  - write commitment levels,
  - create modes,
  - fsinfo property bits.
- Conversion macros map vnode mode/type values to NFSv2/NFSv3 wire values and back.
- `nfstype` enumerates NFS file types.
- `union nfsfh` and `nfsfh_t` define file handle storage.
- Time, 64-bit integer, quad conversion, and special-device structs model packed wire fields.
- `struct nfs_fattr` represents v2/v3 file attributes via a union with accessor macros.
- `struct nfsv2_sattr`, `struct nfsv3_sattr`, `struct nfs_statfs`, `struct nfsv3_fsinfo`, and `struct nfsv3_pathconf` define key protocol payloads.

## Notable Details

- Protocol structs avoid native `quad` fields and use arrays/packed 32-bit components for XDR density.
- `NFSX_FH(v3)` reserves maximum v3 file-handle size plus length field on the client side, while server-side `NFSX_SRVFH(v3)` uses local `fhandle_t` size.
- Generic procedure IDs are used internally, then mapped to v2 wire procedure numbers when needed.
- NFSv2 FIFO mode is encoded as a character-device mode for compatibility.

## Integration

Included by nearly every NFS module. It is the shared contract between NFS marshalling (`nfsm_subs.c`), client vnode/VFS logic, server handlers, and socket/RPC code.
