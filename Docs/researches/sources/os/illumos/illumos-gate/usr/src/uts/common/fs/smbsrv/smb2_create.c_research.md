# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_create.c

Read completely. This file implements the SMB2 `CREATE` command, including request decoding, path extraction, create-context parsing, common open execution, lease/oplock acquisition, durable handle setup or reconnect, and final SMB2 create response encoding.

The main entry point is `smb2_create()`. It decodes the fixed SMB2 create request, validates name offsets and path rules, builds a shadow mbuf for create contexts, then dispatches `smb_common_open()` unless the request is a durable-handle reconnect. It handles protocol-specific validation for impersonation level, oplock level, leases, durable handle v1/v2 contexts, persistent handle flags, delete-on-close, backup intent credentials, query maximal access, on-disk ID responses, and Apple `AAPL` create context replies.

Create-context handling is split into `smb2_decode_create_ctx()`, `smb2_encode_create_ctx()`, `smb2_encode_create_ctx_elem()`, and `smb2_free_create_ctx()`. Supported incoming contexts include EA, security descriptor, durable request/reconnect v1/v2, allocation size, maximal access, timewarp, on-disk ID, leases, and Apple extensions. Unsupported or unknown context IDs are ignored after structural validation. Responses may include maximal access, on-disk ID, Apple extension data, lease state, and durable handle acknowledgements.

Important dependencies are `smb_common_open()`, `smb2_dh_reconnect()`, `smb2_dh_make_persistent()`, `smb2_lease_create()`, `smb2_lease_acquire()`, `smb2_oplock_acquire()`, `smb2_aapl_crctx()`, and SMB mbuf encode/decode helpers. Durable and lease state is stored through `sr->arg.open`, `sr->fid_ofile`, and create-context flags.

Notable behavior: durable reconnect intentionally ignores most create parameters and several context types; persistent durable handles require continuous-availability tree support; EA create contexts are rejected as unsupported; leases are restricted to valid cache-state combinations; non-disk trees and non-regular files suppress oplocks/leases.
