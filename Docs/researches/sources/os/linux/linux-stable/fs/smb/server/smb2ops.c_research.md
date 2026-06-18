# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2ops.c

This file defines SMB2/SMB3 dialect-specific server value tables, operation tables, command dispatch table, and initialization helpers for negotiated SMB dialects.

Dialect value tables:
- `smb21_server_values`
  - SMB 2.1 protocol id, large MTU, SMB2 default I/O sizes, max credits, lock flags, header sizes, response sizes, create-context sizes.
- `smb30_server_values`
  - SMB 3.0 protocol id, SMB3 I/O/trans sizes, SMB3 create lease v2 and durable v2 sizes.
- `smb302_server_values`
  - SMB 3.0.2 values, durable v2 and persistent-handle support size fields.
- `smb311_server_values`
  - SMB 3.1.1 values, same core sizes as SMB3 with SMB 3.1.1 signing/encryption key hooks.

Operation tables:
- `smb2_0_server_ops`
  - SMB2 command extraction, request counter increment, response header/status/allocation/credits, user session/tree connect lookup, SMB2 signing checks and signing response.
- `smb3_0_server_ops`
  - SMB3 signing checks and response signing.
  - SMB 3.0 signing/encryption key generation.
  - Transform header detection, decrypt request, encrypt response.
- `smb3_11_server_ops`
  - SMB 3.1.1 signing/encryption key generation plus transform handling.

Command dispatch table:
- `smb2_0_server_cmds[]`
  - Maps SMB2 command indices to handlers:
    - negotiate
    - session setup
    - tree connect/disconnect
    - logoff
    - create
    - query info
    - query directory
    - close
    - echo
    - set info
    - read/write
    - flush
    - cancel
    - lock
    - ioctl
    - oplock break
    - change notify

Initialization helpers:
- `init_smb2_1_server()`
  - Assigns SMB 2.1 values/ops/commands, HMAC-SHA256 signing, optional leasing capability.
- `init_smb3_0_server()`
  - Assigns SMB 3.0 values/ops/commands, AES-CMAC signing.
  - Enables leasing/directory leasing, encryption, and multichannel based on server flags and client capabilities.
- `init_smb3_02_server()`
  - Similar to SMB3.0, also enables persistent handles when durable-handle flag is set.
- `init_smb3_11_server()`
  - Assigns SMB 3.1.1 values/ops/commands, AES-CMAC signing, leasing, multichannel, durable/persistent handle capability, and initializes preauth session list.
- Runtime tuners:
  - `init_smb2_max_read_size()`
  - `init_smb2_max_write_size()`
  - `init_smb2_max_trans_size()`
  - `init_smb2_max_credits()`

Role:
- Dialect negotiation support: after a client dialect is selected, these helpers attach the correct capabilities, limits, operation hooks, signing/encryption algorithms, and command table to `ksmbd_conn`.

Risk areas:
- The dialect value tables are static globals, and init functions mutate `conn->vals->req_capabilities` by ORing feature bits. Because `conn->vals` points at the shared table, capabilities enabled for one connection can persist for later connections unless reset elsewhere.
- Runtime max-size tuners also mutate shared dialect tables, intentionally affecting subsequent connections globally.
- Command table is shared for SMB2 through SMB3.1.1; dialect-specific behavior is mainly in `conn->ops` and `conn->vals`.
