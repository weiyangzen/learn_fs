# sources/storage-engines/foundationdb/flow/PKey.cpp research

## Purpose

`PKey.cpp` implements Flow wrappers around OpenSSL `EVP_PKEY` public and private keys. It provides PEM/DER decode and encode, public-key extraction from private keys, algorithm identification, digital signing, and signature verification. The wrapper converts OpenSSL failures into FoundationDB `Error` types and rate-limited trace events while storing native key handles in `std::shared_ptr<EVP_PKEY>` with `EVP_PKEY_free` cleanup.

## Important APIs, types, and functions

The public API comes from `PKey.h`: `PKeyAlgorithm`, `pkeyAlgorithmName`, marker structs `PemEncoded` and `DerEncoded`, `PublicKey`, and `PrivateKey`. `PublicKey(PemEncoded, StringRef)` uses `PEM_read_bio_PUBKEY`; `PublicKey(DerEncoded, StringRef)` uses `d2i_PUBKEY`; `writePem` and `writeDer` use `PEM_write_bio_PUBKEY` and `i2d_PUBKEY`; `verify` delegates to `EVP_DigestVerify*`. `PrivateKey` constructors use `PEM_read_bio_PrivateKey` and `d2i_AutoPrivateKey`; `writePem` can optionally encrypt with `EVP_aes_256_cbc` when a password is supplied; `writeDer`, `writePublicKeyPem`, `writePublicKeyDer`, `sign`, `verify`, and `toPublic` expose private-key serialization and signing.

Private helpers `traceAndThrowDecode`, `traceAndThrowEncode`, and `traceAndThrowDsa` read one OpenSSL error from `ERR_get_error`, trace a warning with a suppressed event type, and throw `pkey_decode_error`, `pkey_encode_error`, or `digital_signature_ops_error`. `getPKeyAlgorithm` maps `EVP_PKEY_base_id` to RSA, EC, or unsupported. `doWritePublicKeyPem`, `doWritePublicKeyDer`, and `doVerifyStringSignature` centralize shared public/private operations.

## Control flow

Decode constructors assert non-empty input, create either a memory BIO or DER pointer, ask OpenSSL to parse the key, wrap the returned raw pointer, and reject unsupported algorithms. Encode methods allocate output in a Flow `Arena` after asking OpenSSL or a memory BIO for the encoded size. Signing initializes an `EVP_MD_CTX`, calls digest sign init/update, calls final once to compute signature length, allocates arena bytes, then calls final again to write the signature. Verification follows digest verify init/update/final and returns false for signature mismatch while throwing only for setup/update operational failures.

## State and persistence behavior

Each `PublicKey` or `PrivateKey` object holds shared ownership of an OpenSSL key. Encoded strings and signatures returned from write/sign operations are arena-backed `StringRef`s; callers must keep the `Arena` alive. The code does not persist keys itself. Password-protected private-key PEM output is generated only when the caller passes a non-empty password; the password bytes are copied into a local `std::vector<unsigned char>` for OpenSSL.

## Dependencies and integration points

This file depends on OpenSSL BIO, ERR, EVP, PEM, X509, object, and version headers; Flow `Arena`, `StringRef`, `AutoCPointer`, `Error`, and `TraceEvent`; and the error codes declared elsewhere in Flow. It integrates with TLS/certificate and token/signature code that needs key serialization, public-key distribution, or signature verification. Because it exposes `nativeHandle()`, lower layers can interoperate directly with OpenSSL when necessary.

## Risks and edge cases

Only RSA and EC keys are accepted; Ed25519, DSA, and other OpenSSL key types decode but are rejected as unsupported. `ERR_get_error` consumes a single error from OpenSSL's queue, so traces may omit deeper error stacks. Signature verification deliberately returns `false` for `EVP_DigestVerifyFinal` failure, which is correct for invalid signatures but may also hide some OpenSSL finalization errors if they are reported through the same return path. Arena lifetime is critical for all returned `StringRef` values. `PrivateKey::writePem` uses AES-256-CBC for password encryption; interoperability depends on OpenSSL defaults and caller expectations.

## Test signals

No inline unit tests are present in this file. Useful coverage includes RSA and EC PEM/DER round trips, unsupported algorithm rejection, encrypted and unencrypted private-key PEM writes, sign/verify success and tampered-signature failure across configured digests, `PrivateKey::toPublic` independence from the private key, and trace/error behavior for malformed PEM/DER input.
