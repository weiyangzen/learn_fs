# sources/user-network-fs/libsmb2/examples/smb2-lseek-sync.c

Purpose: This synchronous example demonstrates file-size discovery and `smb2_lseek` behavior.

Important APIs and types: It uses `smb2_open`, `smb2_fstat`, `smb2_lseek`, `smb2_close`, and `struct smb2_stat_64`.

Control flow: The program connects to a share, opens the requested file read-only, obtains size with `smb2_fstat`, seeks to EOF with `SEEK_SET`, seeks back to BOF, then seeks to EOF with `SEEK_END`, printing each resulting offset before cleanup.

State and persistence behavior: It does not mutate the remote file. Runtime state is the SMB context, file handle, stat structure, and current offset.

Dependencies and integration points: It tests the high-level file-handle seek abstraction, which depends on cached file size and offset semantics in libsmb2.

Risks: It prints negative errors using unsigned `PRIu64` formatting in some cases, which can make failures misleading. Error paths can skip some cleanup.

Test signals: For a file of known size, EOF seeks should equal that size and BOF should be zero. Missing path and unsupported seek modes should produce readable errors.
