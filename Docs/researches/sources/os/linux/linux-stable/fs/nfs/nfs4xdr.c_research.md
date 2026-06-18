# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4xdr.c

## Purpose

`nfs4xdr.c` is the Linux NFS client’s NFSv4 XDR implementation. It serializes NFSv4, NFSv4.1, and conditionally NFSv4.2 client requests into RPC COMPOUND calls, decodes server replies, validates returned XDR structure, and registers the client-side RPC procedure table for NFS version 4.

It is not filesystem policy code by itself; it is the protocol marshalling layer used by the rest of the NFS client.

## Main Responsibilities

- Defines encoded and decoded size estimates for each NFSv4 operation and compound procedure.
- Encodes COMPOUND headers, operation headers, state IDs, verifiers, strings, bitmaps, attributes, file handles, names, ACL buffers, layout payloads, and NFSv4.1 session fields.
- Builds compound requests for client operations including READ, WRITE, COMMIT, OPEN, CLOSE, SETATTR, LOOKUP, CREATE, REMOVE, RENAME, LINK, READDIR, READLINK, FSINFO, PATHCONF, STATFS, ACL, SECINFO, delegation return, server capability discovery, migration/fs_locations, and pNFS operations.
- Decodes compound replies in the same operation order used by each encoder.
- Converts protocol status values through `nfs4_stat_to_errno()` and emits tracepoints for XDR status and malformed operation results.
- Provides `nfs4_decode_dirent()` for decoding cached NFSv4 READDIR entries when VFS directory iteration consumes directory pages.
- Exports the `nfs4_procedures[]` procedure table and `nfs_version4` RPC version descriptor.

## Key Data Structures and Constants

- `struct compound_hdr` tracks compound status, operation count, encoded `nops` pointer, tag, expected reply length, and minor version.
- `nfs_type2fmt[]` maps NFSv4 file types such as `NF4REG`, `NF4DIR`, `NF4LNK`, etc. to Linux inode mode type bits.
- Many `*_maxsz` macros define XDR word budgets for individual operations and compound procedures.
- `nfs41_maxwrite_overhead`, `nfs41_maxread_overhead`, and exported `nfs41_maxgetdevinfo_overhead` compute NFSv4.1 RPC overhead for upper layers.

## Encoding Flow

The generic encode path is built around:

- `encode_compound_hdr()` writes tag, minor version, and a placeholder operation count.
- `encode_op_hdr()` writes an NFS operation number and increments the running operation count and expected reply size.
- `encode_nops()` patches the final operation count into the compound header.
- Helpers encode primitive values: `encode_string()`, `encode_uint32()`, `encode_uint64()`, `encode_nfs4_stateid()`, `encode_nfs4_verifier()`, `xdr_encode_bitmap4()`.

Important operation encoders include:

- File identity/path operations: `encode_putfh()`, `encode_putrootfh()`, `encode_getfh()`, `encode_lookup()`, `encode_lookupp()`.
- Data operations: `encode_read()`, `encode_write()`, `encode_commit()`, `encode_readlink()`, `encode_readdir()`.
- Metadata operations: `encode_getattr()`, `encode_getfattr()`, `encode_fsinfo()`, `encode_fs_locations()`, `encode_setattr()`, `encode_attrs()`.
- Namespace operations: `encode_create()`, `encode_remove()`, `encode_rename()`, `encode_link()`.
- State operations: `encode_open()`, `encode_close()`, `encode_open_confirm()`, `encode_open_downgrade()`, `encode_lock()`, `encode_lockt()`, `encode_locku()`, `encode_delegreturn()`.
- NFSv4.0 client identity: `encode_setclientid()`, `encode_setclientid_confirm()`, `encode_renew()`, `encode_release_lockowner()`.
- NFSv4.1 sessions: `encode_exchange_id()`, `encode_create_session()`, `encode_sequence()`, `encode_bind_conn_to_session()`, `encode_destroy_session()`, `encode_destroy_clientid()`, `encode_reclaim_complete()`.
- pNFS: `encode_getdeviceinfo()`, `encode_layoutget()`, `encode_layoutcommit()`, `encode_layoutreturn()`.
- Stateid maintenance: `encode_test_stateid()`, `encode_free_stateid()`.
- Security negotiation: `encode_secinfo()`, `encode_secinfo_no_name()`.

`encode_attrs()` is central for SETATTR/CREATE/OPEN creation attributes. It constructs an attribute bitmap and packed attribute buffer for size, mode, uid/gid owner strings, access/modify times, security labels, and mode+umask where supported. UID/GID mapping failures fall back to `"nobody"`.

## Compound Request Encoders

Each `nfs4_xdr_enc_*()` function constructs one full compound request. Common pattern:

1. Determine minor version from the session via `nfs4_xdr_minorversion()` when applicable.
2. Encode compound header.
3. Encode `SEQUENCE` for NFSv4.1+ sessioned operations.
4. Encode one or more protocol operations in the precise expected server order.
5. Prepare reply pages for variable-size replies when needed.
6. Patch operation count with `encode_nops()`.

Examples:

- READ: `SEQUENCE`, `PUTFH`, `READ`, then prepares reply pages and marks `XDRBUF_READ`.
- WRITE: `SEQUENCE`, `PUTFH`, `WRITE`, optional GETATTR, and marks send buffer `XDRBUF_WRITE`.
- OPEN: `SEQUENCE`, `PUTFH`, `OPEN`, `GETFH`, optional ACCESS, GETATTR, optional LAYOUTGET.
- CLOSE and OPEN_DOWNGRADE may include LAYOUTRETURN before final state operation.
- FS_LOCATIONS handles both migration and lookup-style discovery paths.
- GETACL and fs_locations arrange page-backed receive buffers before decoding variable data.

## Decoding Flow

The generic decode path is built around:

- `decode_compound_hdr()` reads compound status, tag, and operation count.
- `__decode_op_hdr()` validates the returned operation number and operation status. It maps NFS status to Linux errno and records tracepoints for bad status or wrong operation number.
- `decode_op_hdr()` wraps `__decode_op_hdr()`.
- `decode_bitmap4()`, `decode_attr_bitmap()`, `decode_attr_length()`, and `verify_attr_len()` enforce attribute stream structure.
- State helpers set stateid type while decoding: open, lock, delegation, layout, invalid state IDs.

Attribute decoding is strict. Each decoder checks whether earlier unexpected bitmap bits remain, consumes exactly the attribute it owns, clears the consumed bit, and returns either an attribute-valid flag, zero, or an error. `decode_getfattr_attrs()` composes these into `struct nfs_fattr`.

Decoded attribute categories include:

- Type, mode, fileid, mounted_on_fileid, filehandle, fsid, change attr, size.
- Link count, owner, group, raw device, space used, timestamps, security label.
- Server features such as supported attrs, ACL support, case sensitivity, exclusive create support, open argument support.
- FSINFO values such as lease time, max file size, max read/write, time delta, pNFS layout types, layout block size, clone block size, change attribute type, xattr support.
- FS locations and pathnames for migration/referral support.
- pNFS MDS threshold hints.

## Reply Decoders

The `nfs4_xdr_dec_*()` functions mirror each compound encoder’s operation order. They generally stop on required operation failure and decode optional trailing attributes only when appropriate.

Important reply decoders:

- Data paths: `nfs4_xdr_dec_read()`, `nfs4_xdr_dec_write()`, `nfs4_xdr_dec_commit()`.
- Lookup/create/path operations: `nfs4_xdr_dec_lookup()`, `nfs4_xdr_dec_lookupp()`, `nfs4_xdr_dec_lookup_root()`, `nfs4_xdr_dec_create()`, `nfs4_xdr_dec_remove()`, `nfs4_xdr_dec_rename()`, `nfs4_xdr_dec_link()`.
- State paths: `nfs4_xdr_dec_open()`, `nfs4_xdr_dec_open_noattr()`, `nfs4_xdr_dec_open_confirm()`, `nfs4_xdr_dec_close()`, `nfs4_xdr_dec_open_downgrade()`, lock decoders.
- NFSv4.1: exchange/create/destroy session, bind connection, sequence, reclaim complete, destroy clientid.
- pNFS: getdeviceinfo, layoutget, layoutcommit, layoutreturn.
- Security and migration: SECINFO, SECINFO_NO_NAME, FS_LOCATIONS, FSID_PRESENT.
- ACL: GETACL and SETACL.

The READ/READLINK/LAYOUTGET decoders explicitly check whether the server returned more data than was actually received and reject or clamp as appropriate.

## pNFS and Layout Handling

This file supports pNFS protocol marshalling but delegates layout-specific opaque encoding/decoding to layout drivers and page buffers.

- GETDEVICEINFO reads opaque device addresses into pages and validates layout type and notification bitmap.
- LAYOUTGET validates non-empty layout arrays, decodes returned range, iomode, layout type, and opaque layout length, then reads layout bytes from pages.
- LAYOUTCOMMIT encodes whole-file layout commit information plus optional layoutupdate pages.
- LAYOUTRETURN encodes file-level returns and lets the layout driver append private data when available.

## Directory Entry Decode

`nfs4_decode_dirent()` parses one cached NFSv4 directory entry from an XDR stream. It handles EOF/cookie markers, name, attribute bitmap, attributes, file handle, inode number selection, and dentry type derivation.

It fakes inode number `1` when neither mounted-on-fileid nor fileid is available, avoiding inode zero.

## Procedure Registration

The `PROC`, `PROC40`, `PROC41`, and `PROC42` macros populate `nfs4_procedures[]`. Unsupported version-gated entries become stubs. `CONFIG_NFS_V4_2` includes `nfs42xdr.c`, and the procedure table includes v4.2 operations such as SEEK, ALLOCATE, DEALLOCATE, CLONE, COPY, xattrs, READ_PLUS, and ZERO_RANGE when configured.

`nfs_version4` exposes RPC version number 4, procedure count, procedure table, and per-procedure counters.

## Error Handling and Invariants

- XDR reservation failures in `reserve_space()` are treated as impossible sizing bugs and trigger `BUG_ON`.
- Decode paths distinguish transport/XDR corruption (`-EIO`) from protocol status converted via `nfs4_stat_to_errno()`.
- Attribute lengths are verified against stream position to detect malformed or unexpected attribute payloads.
- Returned operation numbers must match expected operation order.
- NFSv4.1 SEQUENCE replies must match expected session ID, slot ID, and sequence number, otherwise `-EREMOTEIO` is returned.
- File handle lengths are rejected when zero or larger than `NFS4_FHSIZE`.
- ACL and page-backed variable replies guard against page buffer overflow/truncation.

## Dependencies

This file depends heavily on Linux SUNRPC XDR helpers, NFS client state/session structures, NFS idmapping, pNFS interfaces, NFSv4 constants, and trace definitions from `nfs4trace.h`.

## Research Notes

This is a high-risk protocol boundary file: correctness depends on exact encode/decode ordering, size estimates, bitmap consumption, and page-buffer setup. Any change to an operation’s compound composition must update both its size macros and its matching decoder order.
