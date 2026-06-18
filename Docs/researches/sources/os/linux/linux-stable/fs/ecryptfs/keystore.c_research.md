# File Research: sources/os/linux/linux-stable/fs/ecryptfs/keystore.c

## Summary
Implements eCryptfs key management and packet handling. It parses and writes OpenPGP-inspired authentication-token packets, retrieves auth tokens from mount-wide lists or the kernel keyring, encrypts/decrypts file encryption keys, communicates with ecryptfsd for public-key operations, and implements FNEK filename packet encryption/decryption.

## Main Responsibilities
- Parse and write variable-length eCryptfs packet sizes.
- Generate and parse tag-1 public-key encrypted FEK packets.
- Generate and parse tag-3 passphrase encrypted FEK packets plus tag-11 signature literal packets.
- Generate tag-64/tag-66 requests and parse tag-65/tag-67 responses for userspace daemon public-key operations.
- Verify auth-token structure versions and token types loaded from user or encrypted keys.
- Look up auth tokens from mount-global registrations or fallback kernel keyring descriptions.
- Decrypt passphrase-encrypted FEKs in kernel with cached Crypto API transforms.
- Decrypt or encrypt public-key FEKs through ecryptfsd messaging when enabled.
- Write and parse tag-70 FNEK encrypted filename packets.
- Generate complete key packet sets for new file headers.
- Register per-file key signatures and mount-wide global auth tokens.

## Key APIs
- `ecryptfs_parse_packet_length()` / `ecryptfs_write_packet_length()`
- `ecryptfs_keyring_auth_tok_for_sig()`
- `ecryptfs_parse_packet_set()`
- `ecryptfs_generate_key_packet_set()`
- `ecryptfs_write_tag_70_packet()`
- `ecryptfs_parse_tag_70_packet()`
- `ecryptfs_add_keysig()`
- `ecryptfs_add_global_auth_tok()`

## Important Behavior
File metadata can contain multiple candidate auth-token packets. `ecryptfs_parse_packet_set()` parses all recognized auth packets, then searches for a matching usable secret. If decryption fails for one candidate, it removes that candidate and tries the next.

Passphrase packet handling uses the session-key encryption key from the auth token to decrypt the FEK with the file cipher. Public-key packet handling sends request packets to userspace and waits for response packets through the messaging subsystem.

Filename encryption with tag 70 uses the mount-wide FNEK signature, requires password auth tokens, prepends deterministic non-null bytes derived from MD5 of the session-key encryption key plus a NUL separator, encrypts the padded filename, and stores the FNEK signature and cipher code in the packet.

## Research Notes
This is the eCryptfs key and packet-format authority. Important correctness points include key semaphore lifetime, `key_put()` pairing, packet boundary checks, encrypted-key size limits, auth-token invalidation on bad payloads, and consistency with `crypto.c` metadata and filename paths.
