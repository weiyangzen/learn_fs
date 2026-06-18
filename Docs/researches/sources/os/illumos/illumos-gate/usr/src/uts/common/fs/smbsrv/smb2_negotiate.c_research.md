# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_negotiate.c

Implements SMB2/SMB3 negotiate handling, including the SMB1 negotiate path that returns an SMB2 response, the initial direct SMB2 negotiate request path, common negotiate response construction, and `FSCTL_VALIDATE_NEGOTIATE_INFO`.

Key behavior:
- Advertises tunable server capabilities and transfer sizes through `smb2srv_capabilities`, `smb2_tcp_bufsize`, `smb2_max_rwsize`, `smb2_max_trans`, and `smb2_old_rwsize`.
- Selects the best supported dialect from `0x202`, `0x210`, `0x300`, `0x302`, `0x311`, bounded by server min/max protocol configuration.
- Parses SMB 3.1.1 negotiate contexts for preauth integrity, encryption capabilities, and signing capabilities, rejecting duplicate or malformed contexts.
- Chooses SHA-512 preauth, a configured encryption cipher, and a configured signing algorithm, with compatibility defaults for older dialects.
- Initializes preauth, signing, encryption mechanisms and socket buffer sizes during negotiation.
- Computes SMB 3.1.1 preauth hashes over request and response messages.
- Drops `VALIDATE_NEGOTIATE_INFO` for SMB 3.1.1, unsigned SMB3 non-encrypted validation, mismatched client security mode/capabilities/GUID, or changed selected dialect.

Important dependencies:
- Protocol encode/decode: `smb_mbc_decodef`, `smb_mbc_encodef`, `smb2_encode_header`, `smb2sr_put_error`.
- Crypto setup: `smb31_preauth_init_mech`, `smb31_preauth_sha512_calc`, `smb2_sign_init_mech`, `smb3_encrypt_init_mech`.
- Session state: `smb_session_t` dialect, capabilities, credits, new request dispatch function, preauth/encryption/signing IDs.

Notable details:
- `SMB2_NEGOTIATE_MAX_DIALECTS` is 64 to match Windows behavior.
- SMB 2.x capabilities are returned as server-supported capabilities, while SMB 3.x capabilities are mostly server/client intersection.
- SMB 3.1.1 negotiate context parsing intentionally gathers data for DTrace before validation errors are returned.
