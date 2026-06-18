# sources/security-integrity/ecryptfs-utils/src/libecryptfs/packets.c

## Purpose
Parses kernel request packets asking userspace key modules to decrypt or encrypt session keys, then builds tag 65 or tag 67 response packets. It is the cryptographic request handler used by the miscdev daemon.

## Important APIs, types, and functions
- `parse_packet` is the public packet dispatcher.
- `key_mod_decrypt` and `key_mod_encrypt` locate the auth token's key module and perform two-pass size-query then output-buffer operations.
- `write_failure_packet`, `write_tag_65_packet`, and `write_tag_67_packet` allocate and fill response messages.

## Control flow
`parse_packet` reads packet type, signature length and signature, key length and key bytes from `emsg->data`. It looks up the signature in the user keyring, reads the auth token, and switches on packet type. Tag 64 requests decrypt an encrypted key and return tag 65. Tag 66 requests encrypt a plaintext key and return tag 67. Any parse, lookup, module, or unknown-type failure writes a failure packet, choosing tag 67 for failed tag 66 requests and tag 65 otherwise.

## State and persistence behavior
Reads the Linux user keyring via `request_key` and `keyctl_read_alloc`. It allocates reply messages and temporary key/signature buffers, and wipes auth-token memory before free. It does not add or remove keys.

## Dependencies and integration points
Depends on keyutils, `messaging.c` packet-length helpers, `key_mod.c` lookup, and module `encrypt`/`decrypt` callbacks. Called by `ecryptfs_run_miscdev_daemon` in `miscdev.c`.

## Risks and edge cases
The parser assumes packet fields are present and does not track the outer message `data_len` while advancing offsets, so malformed short packets can lead to out-of-bounds reads. Failure handling can overwrite the original error code with the status-packet write result. `write_tag_67_packet` sets `data_len` to allocated `data_len` rather than the actual index `i`, which currently matches only if length encoding assumptions hold. Key-module callbacks receive raw blob data from auth tokens and must enforce their own cryptographic validity.

## Test signals
Tests should cover valid tag 64 and tag 66 flows with a stub key module, missing key signatures, malformed packet lengths, too-large encrypted/decrypted output sizes, unknown packet types, failure packet tag selection, and response `data_len` correctness.
