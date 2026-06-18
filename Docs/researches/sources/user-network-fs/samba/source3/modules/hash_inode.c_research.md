# sources/user-network-fs/samba/source3/modules/hash_inode.c

## Purpose
Provides a deterministic synthetic inode generator for named streams and xattr-backed stream views. It hashes the underlying device, inode, and stream name into an `SMB_INO_T`.

## APIs, Types, And Control Flow
The exported API is `SMB_INO_T hash_inode(const SMB_STRUCT_STAT *sbuf, const char *sname)`. It uppercases the stream name with `talloc_strdup_upper`, enters GnuTLS FIPS lax mode, initializes a SHA1 hash, feeds `st_ex_dev`, `st_ex_ino`, and the uppercase name bytes, finalizes into a digest, and copies the leading bytes into the result. On any GnuTLS error it returns zero after cleanup.

## State, Dependencies, Integration
No persistent state is kept. It depends on Samba stat wrappers, talloc, GnuTLS hashing, and Samba's FIPS helper macros. Callers in `vfs_fruit.c` and `vfs_streams_xattr.c` use it to expose stable inode values for alternate data streams.

## Risks And Test Signals
Risks include SHA1 collision possibility, result truncation to `SMB_INO_T`, endian/width differences across platforms, return value zero on hashing failure, and `SMB_ASSERT` abort if name allocation fails. Tests should assert case-insensitive stream-name hashing, different stream names/devices/inodes producing different values, deterministic output within one build, and graceful behavior when GnuTLS initialization fails.
