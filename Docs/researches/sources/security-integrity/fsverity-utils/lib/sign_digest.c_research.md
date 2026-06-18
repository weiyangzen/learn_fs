# sources/security-integrity/fsverity-utils/lib/sign_digest.c

Purpose: This file implements `libfsverity_sign_digest()`, producing Linux fs-verity-compatible PKCS#7 DER signatures over computed file digests.

Important APIs and functions: It validates `libfsverity_digest` and `libfsverity_signature_params`, loads certificates and private keys from PEM files or optional PKCS#11 engine/module/key id settings, constructs the signed data, serializes PKCS#7 DER, and reports OpenSSL errors. It contains engine setup and cleanup paths when OpenSSL engines are available.

Control flow and state: The function allocates output signature memory for the caller, opens crypto/key resources, performs signing, and frees OpenSSL objects on exit. PKCS#11 state is transient but external token configuration influences behavior.

Dependencies and integration points: Depends on OpenSSL/BoringSSL-compatible APIs, public digest structs, CLI `sign`, CLI `enable --signature`, and tests with known certificates/keys.

Risks and test signals: Risks include invalid cert/key handling, PKCS#11 backend availability, OpenSSL API version differences, DER allocation ownership, and leaking sensitive key material. Signals include successful signing tests, invalid key/cert negative tests, and kernel/userspace signature verification compatibility.
