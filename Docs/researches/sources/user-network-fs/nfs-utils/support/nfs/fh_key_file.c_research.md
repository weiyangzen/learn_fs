# sources/user-network-fs/nfs-utils/support/nfs/fh_key_file.c

Purpose: derive a deterministic UUID from a file-handle key file by repeatedly applying UUID version-5/SHA1 generation.

Important API: `int hash_fh_key_file(const char *fh_key_file, uuid_t uuid)`.

Control flow: opens the key file, initializes `uuid` from a fixed seed UUID, reads 256-byte blocks, and for each block calls `uuid_generate_sha1(uuid, uuid, buf, sread)`. Read errors are logged and returned as errno or `EIO`.

State and persistence: reads persistent key-file content and writes the resulting UUID into caller-provided storage. No module-global state.

Dependencies and integration: depends on libuuid, `nfslib.h`, and `xlog`. Used where NFS file-handle signing or identity needs a stable UUID derived from local secret/configured content.

Risks: opens in text mode `"r"` instead of binary mode, which is harmless on Linux but conceptually a byte-hash routine. Empty files produce the fixed seed UUID. Sequential UUID chaining is deterministic but not equivalent to hashing the whole file once with explicit domain separation.

Test signals: missing/unreadable file, empty file, one block, multiple blocks, read error injection, and stable output across runs.
