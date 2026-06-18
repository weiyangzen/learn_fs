<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.cc

## Purpose
Implements `XrdCryptosslRSA`, the OpenSSL EVP-backed RSA key wrapper. It handles key generation, public/private PEM import/export, copy construction, output size calculation, and RSA encryption/decryption/signature-recovery style operations.

## Important APIs, types, and functions
- `XrdCheckRSA()` validates an `EVP_PKEY` with `EVP_PKEY_check`.
- Constructor `(bits, exp)` generates a key pair with minimum/default bit handling and odd exponent enforcement.
- Constructor `(pub,lpub)` imports a PEM public key.
- Constructor `(EVP_PKEY*, check)` adopts an existing key and marks it complete or public depending on validation mode.
- Copy constructor clones through PEM serialization, preserving public-only or private key status.
- `ImportPublic()` and `ImportPrivate()` parse PEM from memory BIOs.
- `GetPublen()`, `ExportPublic()`, `GetPrilen()`, and `ExportPrivate()` size and write PEM buffers.
- `EncryptPublic()`/`DecryptPrivate()` use RSA OAEP padding.
- `EncryptPrivate()`/`DecryptPublic()` use PKCS#1 padding through `EVP_PKEY_sign` and `EVP_PKEY_verify_recover`.
- `GetOutlen()` computes encrypted output capacity based on OAEP payload limits.

## Control flow
Key generation creates a BIGNUM exponent, initializes an RSA keygen context, sets key bits and exponent, generates `fEVP`, then validates the key before marking status complete. Public/private import writes caller bytes into a BIO and reads the corresponding PEM key. Copy construction detects whether the original has a private exponent, writes either public or private PEM to a BIO, and reads it back into a fresh `EVP_PKEY`. Encryption methods validate buffers, create an operation-specific `EVP_PKEY_CTX`, set padding, split input into RSA-sized chunks, and append each encrypted/decrypted block into caller output.

## State and persistence behavior
The object owns `EVP_PKEY *fEVP` and cached exported public/private PEM lengths (`publen`, `prilen`). It stores status in the inherited `XrdCryptoRSA` state. Export methods write PEM into caller-owned buffers and null-terminate. No file persistence occurs in this file, but exported private PEM is sensitive data.

## Dependencies and integration points
Depends on OpenSSL EVP/BIO/PEM/ERR APIs, OpenSSL 3 `core_names.h` for private exponent detection, trace macros, and `XrdCryptoRSA` constants/status. Certificates wrap public keys with `XrdCryptosslRSA(EVP_PKEY*, false)` and attach private keys through this class. The factory exposes all constructors.

## Risks and edge cases
Default constructor does not initialize `fEVP` to null before generation; if early allocation fails, destructor could see indeterminate state unless base construction or compiler behavior masks it. `ImportPrivate()` passes `&fEVP` to `PEM_read_bio_PrivateKey` while a public key may already be stored, requiring careful OpenSSL ownership semantics. Export methods ignore the caller-provided length parameter and assume sufficient space. `GetOutlen()` divides by `EVP_PKEY_size(fEVP)-42`; invalid or very small keys can break this. Encryption loops have non-obvious truncation conditions and may silently return partial data after logging. Private-key "encryption" is signature-like and uses PKCS#1 v1.5 padding; callers should not treat it as confidentiality.

## Test signals
Tests should cover key generation at below-minimum/default/custom sizes, odd/even exponents, public/private PEM round trips, copy of public-only and complete keys, invalid PEM import, OAEP encrypt/decrypt over multi-block input, private/public recover paths, too-small output buffers, ASAN/UBSAN early-failure construction, and OpenSSL 3 private exponent detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.cc -->
