# sources/user-network-fs/impacket/impacket/dpapi.py

## Purpose

`dpapi.py` models Windows DPAPI, credential, vault, and backup-key binary formats and provides key derivation and decryption helpers. It is a parser/decrypter support module for offline Windows secrets workflows: master key files, credential history, DPAPI blobs, vault policy/credential records, CNG key wrappers, known vault schemas, WinCred blobs, PVK/private key blobs, and user password/hash-derived DPAPI keys.

## Important APIs, Types, And Functions

The top-level constants and enums define CryptoAPI algorithm classes/types/SIDs, DPAPI blob flags, WinCred flags/types/persistence, and `ALGORITHMS_DATA`, which maps algorithm IDs to key size, hash/cipher module, cipher mode, IV size, and hash block size. `getFlags()` renders flag enums.

`MasterKeyFile` parses the masterkey file envelope lengths. `MasterKey` parses an encrypted master key, derives cipher material with a PBKDF-like HMAC loop, decrypts with the configured algorithm, validates the embedded HMAC, and stores `decryptedKey`. `CredHist`, `CREDHIST_ENTRY`, and `CREDHIST_FILE` parse and decrypt credential-history chains, deriving later keys from recovered password hashes. `DomainKey` and `DPAPI_SYSTEM` parse domain backup key material and system LSA DPAPI secrets.

`CredentialFile` wraps a credential DPAPI blob. `DPAPI_BLOB` parses protected blob metadata, derives session/cipher keys, decrypts payload data with optional entropy, and verifies the blob signature through two HMAC variants. Vault support includes `VAULT_ATTRIBUTE`, map entries, `VAULT_VCRD`, `VAULT_VPOL`, bcrypt key blob structures, `BCRYPT_KEY_WRAP`, `VAULT_VPOL_KEYS`, known schema structures for Internet Explorer, Windows biometric key, and NGC local account vault entries. `CREDENTIAL_ATTRIBUTE` and `CREDENTIAL_BLOB` parse WinCred records and attributes. `privatekeyblob_to_pkcs1()` converts a Windows private key blob to a PyCryptodome RSA object. `deriveKeysFromUser()` and `deriveKeysFromUserkey()` produce candidate DPAPI keys from password or password hash, including protected-user PBKDF2 variants.

## Control Flow

Parsing is declarative via `impacket.structure.Structure`, with variable-length fields controlled by prior size fields. Most `dump()` methods print decoded fields and hex data. Decryption follows Windows DPAPI layers: caller derives candidate keys from a SID/password/hash, uses `MasterKey.decrypt()` to recover a 64-byte master key, then uses that key with `DPAPI_BLOB.decrypt()` to recover protected blob plaintext. Credential history parsing works backward through length-prefixed entries at the end of the file, tries available keys for each entry, and derives the next generation of keys from recovered hashes.

Vault parsing uses offset maps: `VAULT_VCRD.__init__()` decodes map entries, computes each attribute length from adjacent offsets, instantiates `VAULT_ATTRIBUTE`, and records remaining data. `VAULT_ATTRIBUTE.__init__()` conditionally extends its structure based on raw length, padding sentinel, attribute id, and IV metadata. Known vault schema classes parse decrypted per-schema data. Backup/private key structures are passive except `privatekeyblob_to_pkcs1()`, which converts little-endian RSA fields to a constructed RSA key.

## State And Persistence

The module does not write files or persist recovered secrets. Objects retain parsed raw data, decrypted key material (`MasterKey.decryptedKey`, `CREDHIST_ENTRY.pwdhash/nthash`), parsed attributes, and derived values in memory. Many `dump()` methods print sensitive data to stdout, so caller behavior controls disclosure.

## Dependencies And Integration Points

Dependencies include PyCryptodome hash/cipher/RSA primitives (`HMAC`, `SHA512`, `SHA1`, `MD4`, `AES`, `DES3`, `RSA`), `hashlib.pbkdf2_hmac`, Impacket `Structure`, `hexdump`, UUID formatting, ESE time conversion, RPC SID formatting, and `six` compatibility helpers. Integration points are Impacket examples and tools that parse Windows registry/filesystem artifacts such as masterkey files, `CREDHIST`, Credential Manager blobs, Vault files, DPAPI_SYSTEM secrets, and domain backup keys.

## Risks And Edge Cases

This file handles highly sensitive material; dumps can expose passwords, hashes, master keys, vault keys, and private keys. Cryptographic code is compatibility-focused and accepts legacy algorithms such as 3DES/MD4/SHA1. `deriveKey()` reimplements PBKDF behavior and should be regression-tested because byte-order XOR differs between Python versions. Many constructors assume non-`None` data when checking `len(data)` or parsing nested fields. `DPAPI_BLOB.decrypt()` calls `unpad()` before signature verification, so malformed ciphertext can raise padding errors instead of returning `None`. Enum lookups in dumps can raise if unknown algorithms or credential types appear. Several names contain typos (`Unkown`, `ACCOOUNT`) that are externally visible.

## Test Signals

Strong tests need known Windows fixtures: masterkey decrypt success/failure, DPAPI blob decrypt with and without entropy, credential history chain decrypt, vault VCRD/VPOL parsing, known vault schemas, and private key conversion. Unit tests should cover `deriveKeysFromUser()` for normal and protected-user cases, HMAC validation failures, unknown algorithm handling, malformed variable-length structures, and no-secret logging paths where dumps are not called.
