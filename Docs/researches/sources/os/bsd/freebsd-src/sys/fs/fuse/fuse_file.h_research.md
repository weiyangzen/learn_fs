# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.h

## Purpose
Declares FUSE file-handle types, rationale, structures, conversion helpers, and public file-handle management APIs.

## Main Elements
- Defines `fufh_type_t` for invalid, read-only, write-only, read-write, and exec handles.
- Documents why FreeBSD stores FUSE file handles in vnodes rather than per file descriptor: VOPs often lack `struct file`, but FUSE expects per-open server authorization.
- `struct fuse_filehandle` stores list linkage, daemon-provided 64-bit handle id, FUSE open flags, access type, and credentials/pid used at open time.
- `FUFH_IS_VALID()` validates handle type.
- `fufh_type_2_fflags()` converts handle access type back to open-style flags for FUSE open/create/release requests, deliberately excluding non-access flags.
- Declares lookup, open, init, close, valid-read/write, and lifecycle functions.

## Dependencies And Integration
Included by FUSE vnode, I/O, and file management code. The handle list lives in vnode-private FUSE node data.

## Risk Notes
The header explicitly describes a semantic compromise: handle reuse is keyed by vnode, uid, gid, pid, and access mode, not exact file descriptor. Sending only access-mode flags avoids dangerous mismatches for flags such as `O_APPEND`.
