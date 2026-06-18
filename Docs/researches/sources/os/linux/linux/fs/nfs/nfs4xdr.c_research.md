# File Research: sources/os/linux/linux/fs/nfs/nfs4xdr.c

## Purpose

`nfs4xdr.c` is the Linux NFS client’s NFSv4 XDR implementation. It serializes NFSv4, NFSv4.1, and conditionally NFSv4.2 client requests into RPC COMPOUND calls, decodes server replies, validates returned XDR structure, and registers the client-side RPC procedure table for NFS version 4.

It is the protocol marshalling layer used by the rest of the NFS client, not the higher-level filesystem policy layer.

## Main Responsibilities

- Defines encoded and decoded size estimates for each NFSv4 operation and compound procedure.
- Encodes COMPOUND headers, operation headers, stateids, verifiers, strings, bitmaps, attributes, file handles, names, ACL buffers, layout payloads, and NFSv4.1 session fields.
- Builds compound requests for READ, WRITE, COMMIT, OPEN, CLOSE, SETATTR, LOOKUP, CREATE, REMOVE, RENAME, LINK, READDIR, READLINK, FSINFO, PATHCONF, STATFS, ACL, SECINFO, delegation return, migration/fs_locations, and pNFS operations.
- Decodes compound replies in the same operation order used by each encoder.
- Converts NFS protocol status values through `nfs4_stat_to_errno()` and emits XDR tracepoints for malformed or failed operation replies.
- Provides `nfs4_decode_dirent()` for decoding cached NFSv4 READDIR entries during VFS directory iteration.
- Exports `nfs4_procedures[]` and `nfs_version4`.

## Key Structures and Constants

- `struct compound_hdr` tracks compound status, operation count, encoded `nops` placeholder, tag data, expected reply length, and minor version.
- `nfs_type2fmt[]` maps NFSv4 wire file types to Linux inode mode type bits.
- Many `*_maxsz` macros define XDR word budgets for individual operations and full compound procedures.
- `nfs41_maxwrite_overhead`, `nfs41_maxread_overhead`, and exported `nfs41_maxgetdevinfo_overhead` describe NFSv4.1 RPC overhead for size negotiation.

## Encoding Model

The core encode pattern is:

1. `encode_compound_hdr()` writes tag, minor version, and a placeholder operation count.
2. `encode_op_hdr()` writes each operation number, increments `nops`, and tracks expected reply words.
3. Operation-specific helpers encode arguments.
4. `encode_nops()` patches the final operation count.

Important operation helpers include filehandle/path helpers, data helpers, metadata helpers, state/open/lock helpers, v4.0 client identity helpers, v4.1 session helpers, security negotiation helpers, and pNFS layout helpers.

`encode_attrs()` is central for SETATTR, CREATE, and OPEN create attributes. It constructs an attribute bitmap and packed attribute buffer for size, mode, owner/group strings, timestamps, security labels, and mode+umask when supported. UID/GID mapping failures fall back to `"nobody"`.

## Compound Encoders

Each `nfs4_xdr_enc_*()` function builds one complete COMPOUND request. Common steps are minor-version selection, optional `SEQUENCE`, one or more protocol operations, reply-page setup for variable replies, and final operation-count patching.

Notable compounds:

- READ: `SEQUENCE`, `PUTFH`, `READ`, reply pages, `XDRBUF_READ`.
- WRITE: `SEQUENCE`, `PUTFH`, `WRITE`, optional `GETATTR`, send pages, `XDRBUF_WRITE`.
- OPEN: `SEQUENCE`, `PUTFH`, `OPEN`, `GETFH`, optional `ACCESS`, `GETATTR`, optional `LAYOUTGET`.
- CLOSE and OPEN_DOWNGRADE may include `LAYOUTRETURN` before final state operation.
- FS_LOCATIONS supports both migration and lookup-style discovery.
- GETACL and FS_LOCATIONS arrange page-backed receive buffers before decoding variable data.

## Decoding Model

The generic decode path is strict:

- `decode_compound_hdr()` reads compound status, tag, and operation count.
- `__decode_op_hdr()` validates returned operation number and maps operation status.
- Attribute decoders consume attributes in bitmap order, clear consumed bits, and reject unexpected earlier bits.
- `verify_attr_len()` ensures the decoded attribute payload length exactly matches the server-declared length.
- Stateid decoders tag decoded stateids as open, lock, delegation, layout, or invalid.

Decoded attribute families include file type, mode, fsid, fileid, mounted-on-fileid, filehandle, change attribute, size, link count, owner/group, raw device, space used, timestamps, security labels, supported capabilities, ACL support, case behavior, FSINFO, fs_locations, pNFS layout types, layout block size, clone block size, change-attribute type, xattr support, and pNFS MDS threshold hints.

## Reply Decoders

The `nfs4_xdr_dec_*()` functions mirror their matching encoder order and stop on required operation failure. Major decoder groups cover:

- Data paths: READ, WRITE, COMMIT.
- Namespace paths: LOOKUP, LOOKUPP, LOOKUP_ROOT, CREATE, REMOVE, RENAME, LINK, SYMLINK.
- State paths: OPEN, OPEN_NOATTR, OPEN_CONFIRM, CLOSE, OPEN_DOWNGRADE, LOCK, LOCKT, LOCKU.
- Metadata paths: GETATTR, SETATTR, ACCESS, FSINFO, PATHCONF, STATFS, SERVER_CAPS.
- NFSv4.0 client identity and renew.
- NFSv4.1 sessions: EXCHANGE_ID, CREATE_SESSION, DESTROY_SESSION, SEQUENCE, RECLAIM_COMPLETE, BIND_CONN_TO_SESSION, DESTROY_CLIENTID.
- pNFS: GETDEVICEINFO, LAYOUTGET, LAYOUTCOMMIT, LAYOUTRETURN.
- Security/migration: SECINFO, SECINFO_NO_NAME, FS_LOCATIONS, FSID_PRESENT.
- ACL: GETACL and SETACL.

READ, READLINK, GETDEVICEINFO, and LAYOUTGET guard against servers claiming more data than was actually received.

## pNFS and NFSv4.2 Integration

This file handles pNFS protocol marshalling while leaving layout-driver opaque payloads to layout-specific callbacks and page buffers.

When `CONFIG_NFS_V4_2` is enabled, it includes `nfs42xdr.c`, adding procedure-table entries for SEEK, ALLOCATE, DEALLOCATE, LAYOUTSTATS, CLONE, COPY, OFFLOAD operations, COPY_NOTIFY, LAYOUTERROR, xattrs, READ_PLUS, and ZERO_RANGE.

## Directory Entry Decode

`nfs4_decode_dirent()` decodes one cached NFSv4 directory entry from an XDR stream. It handles EOF/cookie markers, name, attribute bitmap, attributes, filehandle, inode number selection, and dentry type derivation. If no fileid is available, it uses inode number `1` to avoid inode zero.

## Risk Areas

- Encoder and decoder operation order must remain exact for every COMPOUND.
- Size macros must be kept in sync with operation composition.
- Attribute bitmap consumption and `verify_attr_len()` are protocol integrity checks.
- Reply page setup for READ, READDIR, READLINK, GETACL, FS_LOCATIONS, GETDEVICEINFO, and LAYOUTGET is easy to break.
- NFSv4.1 `SEQUENCE` replies must match session ID, slot ID, and sequence number.
- Filehandle length, ACL length, security label length, and page-buffer truncation handling are malformed-server boundaries.
