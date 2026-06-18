# sources/user-network-fs/samba/source3/modules/hash_inode.h

## Purpose
Declares the synthetic inode hash helper used by stream-capable VFS modules.

## APIs, Types, And Control Flow
Exports `SMB_INO_T hash_inode(const SMB_STRUCT_STAT *sbuf, const char *sname)`. The function takes an existing Samba stat buffer and stream/xattr name, and returns an inode-sized deterministic hash. There is no inline logic.

## State, Dependencies, Integration
The header has no state. It relies on prior inclusion of Samba type definitions for `SMB_INO_T` and `SMB_STRUCT_STAT`, commonly supplied by `includes.h`. It is included by `vfs_fruit.c`, `vfs_streams_xattr.c`, and the implementation file.

## Risks And Test Signals
The main risk is type-context fragility if included without Samba base headers. Compile tests should include it from modules that use stream inode synthesis and validate ABI consistency with `hash_inode.c`.
