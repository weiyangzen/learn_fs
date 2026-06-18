# sources/distributed-fs/xrootd/python/src/PyXRootDAdler32.cc

## Purpose
This source exposes a simplified Python API to write an Adler-32 checksum extended attribute for a local file using XRootD checksum attribute structures.

## Important APIs, Types, and Functions
`setXAttrAdler32_cpp(path, checksum)` parses two strings, validates an 8-character checksum, opens the file read-only, `fstat`s it, populates `XrdOucXAttr<XrdCksXAttr>`, writes the structured attribute through `xCS.Set("", fd)`, best-effort removes legacy `user.checksum.adler32`, and returns `None` or raises Python exceptions.

## Control Flow
The function performs argument validation first, then local filesystem operations. Every failing syscall preserves `errno` across `close` before raising `OSError`. Attribute setup failures raise `RuntimeError`. Platform-specific legacy removal uses `fremovexattr` on Linux/GNU or `openat`/`unlinkat` on Solaris-like systems.

## State and Persistence
It persists checksum metadata in the file's extended attributes and may remove an older xattr name. It opens and closes a file descriptor each call. It uses the file modification time to set checksum metadata timestamps.

## Dependencies and Integration Points
Depends on POSIX file APIs, optional platform xattr APIs, `XrdCksXAttr`, and `XrdOucXAttr`. Registered as a module method in `PyXRootDModule.cc`.

## Risks and Test Signals
Validation only checks checksum length, while `XrdCksXAttr::Set` appears to validate content later. The code assumes local filesystem xattr support and sufficient permissions. Tests should cover success on an xattr-capable filesystem, invalid length, invalid hex value, nonexistent file, permission errors, and legacy xattr cleanup behavior on supported platforms.
