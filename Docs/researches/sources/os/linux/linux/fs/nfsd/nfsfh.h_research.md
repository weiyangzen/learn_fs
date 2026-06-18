# File Research: sources/os/linux/linux/fs/nfsd/nfsfh.h

## Summary
Defines the on-wire and internal NFSD filehandle representation, fsid encodings, `svc_fh` state, and inline helpers for initialization, matching, write access, hashing, and attribute bookkeeping.

## Main Responsibilities
- Documents and defines `struct knfsd_fh`, whose first bytes describe version, auth type, fsid type, and fileid type.
- Defines `struct svc_fh`, the internal verified filehandle object carrying handle bytes, dentry/export references, WCC state, write-mount state, and NFSv4 post/pre change attributes.
- Provides fsid encodings for device, user fsid, deprecated major/minor, encoded device, UUID-derived, full UUID, and UUID-plus-inode formats.
- Exposes core filehandle operations implemented in `nfsfh.c`.
- Provides small helpers for copying, initialization, comparison, fsid comparison, mount write acquisition, CRC hashing, and WCC reset.

## Key Data Structures and Interfaces
- `struct knfsd_fh` stores up to `NFS4_FHSIZE` raw bytes and current size.
- `struct svc_fh` stores raw handle plus validated VFS/export context.
- `enum nfsd_fsid` identifies fsid encoding in the handle.
- `enum fsid_source` tells NFSv2 attribute encoding whether fsid came from device, explicit fsid, or UUID.
- `mk_fsid()` serializes the selected fsid representation into handle words.
- `key_len()` returns fsid encoding byte lengths.

## Important Behavior
All handle words are treated as opaque to clients, but internal code sometimes stores host-endian and network-endian values in the same raw word array. The comments call this out explicitly, and the helpers use forced casts where needed.

`fh_want_write()` and `fh_drop_write()` protect exported mounts from writes during remount or shutdown. The flag in `svc_fh` prevents duplicate mount write acquisition.

`knfsd_fh_hash()` computes a Wireshark-compatible CRC32 hash for tracing/debugging. `fh_match()` and `fh_fsid_match()` compare exact raw handles or only fsid portions.

## Dependencies
Depends on Linux crc32, SunRPC service structures, inode versioning, exportfs fid formats, NFSv4 constants, and NFSD export definitions.

## Risks and Subtleties
`fh_copy()` warns if the source has a verified dentry; it is intended for raw decoded handles, not transferring live references. Misusing shallow copies can leak or double-drop dentries/exports.

`mk_fsid()` assumes UUID pointers are valid for UUID modes and uses direct casts into raw handle storage. Callers must choose an fsid type that is valid for the export and handle size.
