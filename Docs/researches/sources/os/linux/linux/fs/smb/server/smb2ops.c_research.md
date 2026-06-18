# File Research: sources/os/linux/linux/fs/smb/server/smb2ops.c

This file defines per-dialect SMB2/SMB3 server values, operations, command dispatch tables, and runtime tuners for I/O sizes and credits.

Dialect values:
- SMB 2.1 uses large MTU, SMB2 default I/O sizes, HMAC-SHA256 signing, and lease-size v1 create contexts.
- SMB 3.0 and 3.0.2 use SMB3 I/O sizes, AES-CMAC signing, encryption-capable ops, durable v2 context sizing, and optional directory leasing/encryption/multichannel/persistent handles depending on global flags and client capabilities.
- SMB 3.1.1 uses SMB3 sizes, AES-CMAC signing in this setup, SMB 3.1.1 signing/encryption key generation hooks, preauth session table initialization, and optional leasing/multichannel/persistent handles.

Operation tables:
- SMB2 ops include command extraction, request counters, response header/status setup, response allocation, credits, session/tcon lookup, signing checks, and signing response generation.
- SMB3 ops add SMB3 signing checks, SMB3 signing responses, signing/encryption key generation, transform-header detection, decrypt request, and encrypt response.
- SMB3.1.1 swaps in SMB3.1.1 key derivation functions.

Command dispatch:
- One command table maps SMB2 command indexes to handlers: negotiate, session setup, tree connect/disconnect, logoff, create, query info, query directory, close, echo, set info, read, write, flush, cancel, lock, ioctl, oplock break, and change notify.

Initialization functions:
- `init_smb2_1_server`, `init_smb3_0_server`, `init_smb3_02_server`, and `init_smb3_11_server` assign per-connection values, ops, command table, max command count, signing algorithm, and advertised capabilities.
- Capability advertisement depends on `server_conf.flags` and client capabilities.

Runtime tuners:
- `init_smb2_max_read_size`, `init_smb2_max_write_size`, and `init_smb2_max_trans_size` clamp values between SMB3 min/max I/O sizes and apply them to all dialect tables.
- `init_smb2_max_credits()` updates max credits for all dialect tables.

Role in this group:
- Supplies the protocol ops consumed by `server.c`.
- Uses `server.h` global configuration.
- Selects capabilities that affect `oplock.c` lease behavior, durable handles, multichannel, signing, encryption, and credit processing.
