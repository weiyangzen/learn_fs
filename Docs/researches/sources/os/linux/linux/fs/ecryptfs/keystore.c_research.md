# File Research: sources/os/linux/linux/fs/ecryptfs/keystore.c

## Purpose
Implements eCryptfs in-kernel key management and packet parsing/writing for authentication tokens, encrypted file encryption keys, public-key userspace daemon interaction, passphrase packet handling, and filename-encryption tag-70 packets.

## Main Responsibilities
- Encode and decode OpenPGP-inspired packet lengths.
- Parse tag 1, 3, 11, 65, 67, and 70 packet formats.
- Write tag 1, 3, 11, 64, 66, and 70 packet formats.
- Retrieve and validate auth tokens from mount-global token lists or Linux keyrings.
- Decrypt file encryption keys from passphrase or private-key auth tokens.
- Generate key packet sets for new encrypted files.
- Add key signatures and mount-wide auth-token entries.

## Packet Roles
- Tag 1: public-key encrypted file encryption key metadata.
- Tag 3: passphrase encrypted file encryption key metadata.
- Tag 11: literal packet used here to store authentication-token signatures after tag 3.
- Tag 64/65: kernel-to-userspace and userspace-to-kernel packets for private-key decrypt.
- Tag 66/67: kernel-to-userspace and userspace-to-kernel packets for private-key encrypt.
- Tag 70: FNEK-encrypted filename packet embedded in encrypted dentry names.

## Key Lookup and Validation
`ecryptfs_keyring_auth_tok_for_sig()` first requests a user key by signature, then tries encrypted-key type support if configured. It locks the key semaphore for write and validates payload type/version with `ecryptfs_verify_auth_tok_from_key()`.

`ecryptfs_find_global_auth_tok_for_sig()` searches mount-registered tokens, validates key liveness, locks the key, verifies payload, returns a key reference, and invalidates broken tokens. `ecryptfs_find_auth_tok_for_sig()` uses mount-global tokens first and optionally falls back to the user keyring unless `ECRYPTFS_GLOBAL_MOUNT_AUTH_TOK_ONLY` is set.

## File Metadata Parsing
`ecryptfs_parse_packet_set()` walks auth-token packets from a metadata buffer. It parses tag 3 plus following tag 11 signature packets, or tag 1 packets. It then searches for a matching real auth token, decrypts the candidate encrypted FEK with passphrase or private-key support, computes the root IV, and initializes the file crypto context.

If decryption fails for one candidate token, that token is removed from the temporary list and the function searches for another candidate. Temporary auth-token list entries are wiped and freed before returning.

## File Metadata Generation
`ecryptfs_generate_key_packet_set()` iterates the inode `crypt_stat->keysig_list`, retrieves each mount-global auth token, and writes:
- tag 3 plus tag 11 for password tokens,
- tag 1 for private-key tokens, using userspace daemon encryption if needed.

It appends a zero boundary byte if space remains and reports the total bytes written.

## Passphrase Handling
`write_tag_3_packet()` encrypts the file encryption key with the passphrase token’s session-key encryption key and writes cipher/S2K/hash/salt/iteration metadata. `decrypt_passphrase_encrypted_session_key()` reverses this by using a cached skcipher transform, decrypting the encrypted key into the auth token, and copying it to `crypt_stat->key`.

## Private-Key / Userspace Daemon Handling
Private-key operations use messaging:
- `decrypt_pki_encrypted_session_key()` writes tag 64, sends it to `ecryptfsd`, waits for tag 65, parses the decrypted FEK, and updates `crypt_stat`.
- `pki_encrypt_session_key()` writes tag 66, sends it to userspace, waits for tag 67, and fills an `ecryptfs_key_record`.

These paths require `CONFIG_ECRYPT_FS_MESSAGING` support and a connected daemon for the effective user.

## Filename Encryption
`ecryptfs_write_tag_70_packet()` finds the mount FNEK auth token, gets the filename cipher transform, computes block-aligned plaintext as random/non-null prefix plus NUL separator plus filename, writes tag 70 metadata, and encrypts the block-aligned filename with the FNEK session-key encryption key.

`ecryptfs_parse_tag_70_packet()` validates tag and length, extracts FNEK signature and cipher code, finds the auth token, decrypts the block-aligned filename, scans for the NUL separator, validates resulting plaintext size, and returns a newly allocated plaintext name.

## State and Locking
- Key payloads are protected by key semaphore locking around auth-token access.
- Mount-global auth token list has `global_auth_tok_list_mutex`.
- Inode key signature list has `keysig_list_mutex`.
- Cached crypto transforms use the transform-specific mutex returned by `ecryptfs_get_tfm_and_mutex_for_cipher_name()`.

## Error Handling and Edge Cases
- Five-byte packet lengths are not supported.
- Unsupported hash algorithms and unsupported S2K IDs are rejected.
- Filename encryption supports password tokens only.
- Private-key paths depend on userspace daemon responses and return I/O errors on missing or malformed responses.
- Packet parsing performs max-size checks before copying key material.

## Risks and Notes
- MD5 and RFC2440-era packet formats are compatibility constraints.
- Some debug paths can log key material when verbosity is enabled.
- `write_tag_3_packet()` uses cached or prior session-key encryption key material; correctness depends on user key payload preparation by userspace tools.
- Public-key support is split between kernel packet framing and userspace daemon cryptographic operations.
