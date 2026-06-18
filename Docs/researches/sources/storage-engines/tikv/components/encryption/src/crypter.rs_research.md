# sources/storage-engines/tikv/components/encryption/src/crypter.rs

Purpose: This module contains encryption primitive helpers: key length mapping, file encryption metadata, IV handling for CTR/GCM modes, AES-GCM tag handling, an AES-256-GCM crypter, and config validation.

Important APIs and types: Functions include `get_method_key_length` and `verify_encryption_config`. Types include `FileEncryptionInfo`, `Iv::{Gcm,Ctr,Empty}`, `AesGcmTag`, and `AesGcmCrypter<'k>`. `AesGcmCrypter::KEY_LEN` is 32 bytes and it exposes `new`, `encrypt`, and `decrypt`.

Control flow: IV constructors use OpenSSL random bytes. `Iv::from_slice` interprets 16 bytes as CTR and 12 bytes as GCM. CTR `add_offset` treats the IV as a big-endian `u128` and wraps addition; GCM and empty IVs reject offset changes. AES-GCM uses OpenSSL AEAD functions with empty AAD, returning ciphertext plus a 16-byte tag.

State and persistence behavior: `FileEncryptionInfo` carries method/key/iv metadata and hides key material in `Debug`. No persistent state is stored here; callers persist encrypted metadata elsewhere.

Dependencies and integration points: It uses `kvproto::EncryptionMethod`, `cloud::kms::PlainKey`, OpenSSL random and symmetric APIs, byteorder, and crate errors.

Risks: `get_method_key_length` panics on unknown methods. `AesGcmTag::from` asserts the source is at least 16 bytes but then attempts to copy the whole source into 16 bytes, so longer slices would panic. GCM uses no AAD, so all authenticated context must be inside ciphertext or external protocol checks.

Test signals: Tests check random IV uniqueness/roundtrip, NIST AES-256-GCM vector encryption/decryption, tag equality, and decryption failure with a wrong tag.
