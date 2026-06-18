# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.h

## Purpose

Declares SMBFS shared helper types, search context state, SMB wire-operation prototypes, time/path/name conversion helpers, and malloc types.

## Main Interface

Memory types:
- `M_SMBFSDATA`
- `M_SMBFSCRED`

`struct smbfattr` carries DOS attributes, size, atime/ctime/mtime, and pseudo inode.

Directory search:
- `SMBFS_RDD_*` flags describe findfirst/findnext state.
- `struct smbfs_fctx` stores wildcard, attr mask, share/credential, active request pointer, response counters, search key, fixed/allocated filename buffers, search id, info level, resume-name state, and current returned attrs/name.

Declared SMB-level operations:
- locking, statfs, file size.
- path and file attribute/timestamp setters.
- open/close/create/delete/flush/rename/move/mkdir/rmdir.
- findopen/findnext/findclose and lookup.
- full path construction and filename conversion.
- SMB time conversions.
- SMB credential allocation/free.

## Integration Points

Included by SMBFS node, I/O, request, and vnode operation files. It is the main internal API between VFS-facing SMBFS code and SMB wire request construction.

## Risks and Review Notes

The search context contains a union of request types and dialect-dependent fields. Correct cleanup requires matching the chosen search mode so outstanding request objects, server search handles, resume names, and allocated name buffers are all released.
