<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/PKey.h -->
# sources/storage-engines/foundationdb/flow/include/flow/PKey.h

Purpose: This header wraps OpenSSL public and private key handling for Flow. It provides RAII-style `PublicKey` and `PrivateKey` value handles that read and write PEM/DER encodings, expose algorithm metadata, and perform digest signing and verification.

Important APIs and types: `PKeyAlgorithm` classifies keys as `UNSUPPORTED`, `RSA`, or `EC`; `pkeyAlgorithmName` returns display names. Marker types `PemEncoded` and `DerEncoded` select constructors. `PublicKey` exposes PEM/DER constructors, `writePem`, `writeDer`, `algorithm`, `algorithmName`, `verify`, `nativeHandle`, and `operator bool`. `PrivateKey` adds private-key PEM/DER writers, public-key extraction writers, `sign`, `verify`, and `toPublic`.

Control flow: Constructors consume encoded `StringRef` input and initialize a shared `EVP_PKEY`. Writer methods allocate encoded bytes into a supplied `Arena`. Signing and verification use OpenSSL `EVP_DigestSign*` and `EVP_DigestVerify*` with a caller-provided digest.

State and persistence behavior: The in-memory state is a `std::shared_ptr<EVP_PKEY>`. Persistent state is external key material in PEM or DER form returned through arena-backed `StringRef`. Password support exists for private PEM output. Default-constructed keys are empty and check false.

Dependencies and integration points: It depends on OpenSSL EVP APIs and Flow `Arena`/`StringRef`. It supports TLS, authentication, token validation, and any code needing asymmetric signatures without exposing OpenSSL ownership details.

Risks: `nativeHandle()` exposes the raw OpenSSL pointer, so callers can violate wrapper invariants if they mutate or free it incorrectly. Arena-returned encodings require the arena to outlive the `StringRef`. Unsupported algorithms must be handled by callers. OpenSSL error handling is implemented in the source file and should be verified for malformed input.

Test signals: Key tests include PEM and DER read/write round trips for RSA and EC keys, sign/verify success and failure, password-protected private PEM output, algorithm reporting, empty-key behavior, and malformed key input errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/PKey.h -->
