# sources/user-network-fs/impacket/impacket/dpapi_ng.py

## Purpose

`dpapi_ng.py` implements pieces of DPAPI-NG group key derivation and content decryption. It parses DPAPI-NG key identifiers and encrypted password blobs, creates security descriptors for group key access, derives L2 and KEK material from GKDI group key envelopes, unwraps content encryption keys with AES Key Wrap, and decrypts AES-GCM ciphertext.

## Important APIs, Types, And Functions

`SP800_108_Counter()` is a local NIST SP 800-108 counter-mode KDF variant that permits NUL bytes in label/context. `KeyIdentifier` parses version, magic, flags, L0/L1/L2 indices, root key id, unknown/public-key bytes, domain, and forest; `is_public_key()` checks the low flags bit. `EncryptedPasswordBlob` parses timestamp parts, length, flags, and blob data.

Security descriptor helpers `create_ace()` and `create_sd()` build LDAP security descriptor objects granting the target SID mask `3` and Everyone mask `2`, owned/grouped by Local System. KDF helpers include `int_to_u32be()`, `compute_kdf_hash()`, `compute_kdf_context()`, and `kdf()` with SHA512/SHA256 HMAC selection. `compute_l2_key()` walks GKDI L1/L2 indices to derive the requested L2 key. `generate_kek_secret_from_pubkey()` handles finite-field DH public-key KEK secret derivation and stubs ECDH. `compute_kek()` chooses public-key or symmetric-secret context, then derives a 32-byte KEK. `aes_unwrap()`, `unwrap_cek()`, and `decrypt_plaintext()` handle key unwrap and AES-GCM plaintext decryption.

## Control Flow

Typical decrypt flow is: parse a `KeyIdentifier`, obtain a `GroupKeyEnvelope`, call `compute_kek()` to derive a KEK, call `unwrap_cek()` on the encrypted content key, then call `decrypt_plaintext()` with CEK, IV, and encrypted blob. `compute_l2_key()` compares the envelope indices with the key identifier, reseeds L2 when necessary, walks L1 downward through KDF calls, optionally regenerates L2 at index 31, then walks L2 downward until it reaches the requested index. Public-key identifiers call `generate_kek_secret_from_pubkey()`, which derives a private key from the L2 key, computes a DH shared secret from `FFCDHKey` public parameters, hashes it into a KEK secret, and feeds that into the final KDF.

## State And Persistence

The module is stateless. All derived keys, security descriptors, parsed structures, and plaintexts are returned in memory only. It does not cache group keys, persist security descriptors, or authenticate decrypted plaintext beyond the AES-GCM decrypt primitive used.

## Dependencies And Integration Points

It depends on Impacket GKDI structures (`ECDHKey`, `FFCDHKey`, `GroupKeyEnvelope`), LDAP security descriptor/ACE/SID types, Impacket `Structure`, and PyCryptodome SHA/HMAC/AES helpers. It integrates with code that talks to GKDI (`gkdi.py`) or parses DPAPI-NG protected blobs, especially workflows that need to compute a KEK from group key envelopes and unwrap/decrypt password blobs.

## Risks And Edge Cases

ECDH public-key mode is explicitly unsupported and returns `None`; callers of `compute_kek()` can fail later if they do not check for that. `decrypt_plaintext()` uses AES-GCM `decrypt()` without verifying an authentication tag, so integrity is not checked here. `kdf()` defaults silently to SHA512 for unknown hash strings that do not include `SHA256`. `aes_unwrap()` returns `None` on AIV mismatch, while `unwrap_cek()` raises; callers need consistent error handling. Index-walking assumes the requested indices are reachable by decrementing from envelope indices and does not guard against underflow/mismatched envelopes. Public-key DH shared-secret conversion may produce a zero-length byte string for a zero shared secret.

## Test Signals

Tests should use known GKDI/DPAPI-NG vectors for L2 derivation, symmetric KEK derivation, finite-field DH public-key KEK derivation, AES unwrap success/failure, and encrypted password blob decryption. Unit tests should cover SHA256 vs SHA512 KDF selection, ECDH unsupported behavior, mismatched key indices, malformed key identifier variable lengths, and AES-GCM tag-verification expectations at the caller boundary.
