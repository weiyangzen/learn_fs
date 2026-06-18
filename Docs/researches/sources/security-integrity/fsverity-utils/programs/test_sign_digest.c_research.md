# sources/security-integrity/fsverity-utils/programs/test_sign_digest.c

Purpose: This test program validates `libfsverity_sign_digest()` with fixture digests, certificate/key inputs, and invalid parameter cases.

Important APIs and functions: It constructs `libfsverity_digest` and `libfsverity_signature_params`, invokes signing, checks signature allocation/size, and verifies expected failures for missing or malformed inputs.

Control flow and state: Each test signs or rejects local fixture data. Allocated DER signature buffers are freed by the test. No kernel state is required.

Dependencies and integration points: Depends on OpenSSL-enabled builds and certificate/key test fixtures. It protects CLI `sign` and `enable --signature` interoperability.

Risks and test signals: Crypto backend differences may affect availability or DER details. Signals include nonempty DER output, correct negative errno classes, and clean behavior when optional PKCS#11 support is absent.
