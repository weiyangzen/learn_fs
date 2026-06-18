# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr.h

## Purpose

Declares HFS+ xattr handlers and internal xattr helper APIs shared by the namespace-specific handler files and the core xattr implementation.

## API Surface

Exports declarations for `hfsplus_xattr_osx_handler`, `hfsplus_xattr_user_handler`, `hfsplus_xattr_trusted_handler`, `hfsplus_xattr_security_handler`, and the handler array. It declares internal and prefixed set/get helpers, listxattr, and `hfsplus_init_security()`.

## Dependencies

Includes `<linux/xattr.h>` and relies on HFS+ inode/superblock types being visible to C files including this header.

## Risks

This header is the namespace-handler contract. Signature drift between VFS xattr handler callbacks and these declarations would break compilation across all HFS+ xattr files.
