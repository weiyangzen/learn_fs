<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.cc

## Purpose
Implements `XrdCryptosslCipher`, the OpenSSL EVP-backed symmetric cipher and Diffie-Hellman key agreement implementation for XRootD. It supports local random-key ciphers, imported ciphers, serialized bucket round trips, DH public key exchange, IV management, and encrypt/decrypt buffer sizing.

## Important APIs, types, and functions
- `getFixedDHParams()` returns a process-static OpenSSL `EVP_PKEY` containing hardcoded 3072-bit DH parameters.
- `XrdCheckDH()` validates DH parameters, skipping expensive checks when the fixed parameters match.
- Constructors initialize ciphers from a type/length, from explicit key+IV, from `XrdSutBucket`, or for DH key agreement.
- `Finalize()` completes DH key agreement using a peer public buffer and initializes the symmetric cipher key from the derived secret.
- `Public()` exports DH parameters plus public key hex between `---BPUB---` and `---EPUB---` markers.
- `AsBucket()` serializes type, IV, key bytes, and optional DH p/g/pub/priv bignums into a `kXRS_cipher` bucket.
- `SetIV()`, `RefreshIV()`, and `GenerateIV()` manage IV state.
- `Encrypt()`, `Decrypt()`, and internal `EncDec()` run `EVP_CipherUpdate` and `EVP_CipherFinal_ex`.
- `EncOutLength()`, `DecOutLength()`, and `MaxIVLength()` provide caller buffer sizing hints.

## Control flow
Normal cipher construction resolves the requested cipher name, defaulting to `bf-cbc`, generates random key material with `XrdSutRndm::GetBuffer`, creates an `EVP_CIPHER_CTX`, optionally sets a non-default key length, stores the selected key in the base-class buffer, and generates a fresh IV. Import construction copies caller-provided key and IV, initializes the EVP context, and records whether default key length is used. Bucket construction parses a custom binary layout of seven `kXR_int32` lengths followed by type, IV, key, and DH bignum hex strings, reconstructing the DH key via OpenSSL 3 `OSSL_PARAM` APIs or legacy DH APIs. DH construction without a peer generates a key pair using fixed parameters; with a peer it parses the peer's exported parameters/public key, generates a local key pair, derives a shared secret, and uses that as symmetric key material. `Finalize()` repeats the peer-public parsing and derive flow for objects that already hold local DH state. Encryption/decryption reinitializes the EVP context for every operation with the current key and IV, then performs update/final.

## State and persistence behavior
The class stores mutable `fIV`, IV length, `cipher`, `ctx`, optional DH key `fDH`, default-length flag, and validity flag. Key bytes and type live in the inherited `XrdCryptoCipher` buffer/type storage. Serialized buckets persist sensitive material: they may include symmetric key bytes and DH private key bignums. `Public()` returns a caller-owned heap buffer. `RefreshIV()` returns the internal IV pointer, not a copy. The fixed DH parameter object is a process-static OpenSSL allocation intended to live for process lifetime.

## Dependencies and integration points
Depends on OpenSSL EVP, DH, PEM, BIO, and OpenSSL 3 provider parameter APIs; `XrdSutRndm` for random keys/IVs; `XrdSutBucket` via the base interface; and cryptossl trace macros. `XrdCryptosslFactory` constructs this class for all cipher factory methods and exposes padding support. The DH public export format is a private protocol consumed by the same class on the peer side.

## Risks and edge cases
The default cipher is Blowfish CBC (`bf-cbc`), a legacy algorithm; security-sensitive callers should request modern ciphers if available. `strcpy(cipnam,t)` is bounded only after copying, so cipher names longer than 63 bytes can overflow before `cipnam[63]=0`. Bucket parsing increments `cur` twice after IV copy, which can desynchronize subsequent reads. `AsBucket()` assumes `fDH` is present when extracting DH bignums; a valid non-DH symmetric cipher may dereference a null `fDH`. Serialized buckets contain private material in cleartext and need transport/storage controls. Some BIO and OpenSSL allocation failure paths leak partially allocated resources or continue after null parameter-builder pointers. `Finalize()` frees `ctx` on invalid results but assumes `ctx` was created by the DH constructor. IV generation always uses `EVP_MAX_IV_LENGTH`, not the selected cipher's actual IV length.

## Test signals
Tests should round-trip supported ciphers through constructor, explicit import, and bucket serialization; validate long cipher names under ASAN; verify DH public exchange between two objects with padded and unpadded derivation; compare behavior under OpenSSL 1.1 and 3.x; test `AsBucket()` on non-DH ciphers; check encryption/decryption with refreshed IVs; and fuzz malformed bucket lengths/public key markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.cc -->
