# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libsec.h

Drawterm copy of Plan 9 libsec cryptography and TLS interface declarations.

Key contents:
- Defines state structs and APIs for AES-CBC, Blowfish CBC/ECB, DES, 3DES, MD4, MD5, SHA1, HMAC-MD5, HMAC-SHA1, random generation, RC4, prime generation, RSA, ElGamal, DSA, X.509 parsing/generation/verification, PEM decoding, TLS client/server handshakes, thumbprints, and certificate reading.
- Integrates with `mpint` multiprecision integers from `mp.h`.

Role in this group:
- Supplies cryptographic APIs used by authentication, TLS, and secure channel code in drawterm.

Notable risks:
- Exposes legacy/insecure primitives including DES, RC4, MD4, and SHA1-era X.509 thumbprints.
- Header has no include guard beyond relying on `_MPINT` for forward declaration behavior.
