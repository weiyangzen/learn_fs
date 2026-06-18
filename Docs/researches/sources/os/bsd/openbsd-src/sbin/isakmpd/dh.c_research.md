# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.c

This file implements Diffie-Hellman group support for `isakmpd`.

Key responsibilities:
- Defines supported IKE DH groups, including MODP groups 1, 2, 5, 14-18 and elliptic-curve groups 19-21 and 26-30, with optional EC2N groups when OpenSSL supports them.
- Instantiates group objects by numeric group ID.
- Initializes MODP or EC group-specific state.
- Generates public exchange values.
- Computes shared secrets.
- Converts EC points between raw IKE wire format and OpenSSL `EC_POINT`.

Important data and functions:
- `ike_groups[]`: group metadata including type, ID, bit size, MODP prime/generator strings, or EC NID.
- `group_get()`: finds group metadata, allocates `struct group`, assigns function pointers, and initializes it.
- `group_free()`: frees DH/EC state and group memory.
- `dh_getlen()`, `dh_secretlen()`, `dh_create_exchange()`, `dh_create_shared()`: generic wrappers.
- `modp_init()`: builds OpenSSL `DH` parameters from hex prime/generator.
- `modp_create_exchange()`: generates DH public key and zero-pads to fixed group length.
- `modp_create_shared()`: computes shared key and zero-pads.
- `ec_init()`: creates and validates an EC key for the configured curve.
- `ec_getlen()` and `ec_secretlen()`: compute public exchange and shared-secret sizes.
- `ec_create_exchange()`: serializes the local EC public point.
- `ec_create_shared()`: validates peer point, multiplies by private key, and serializes x-coordinate only.
- `ec_point2raw()` and `ec_raw2point()` handle fixed-width EC coordinate serialization.

Notable behavior:
- ECP shared secret uses only the x-coordinate per RFC 5903.
- EC peer public keys are validated through an `EC_KEY` wrapper before shared secret computation.
- Sensitive BIGNUMs and EC points are cleared during cleanup.
- `DH_MAXSZ` in the header allows up to 8192-bit MODP output.

Dependencies:
- OpenSSL DH, EC, ECDH, BN, and object NID APIs.
- `dh.h` structures.

Research notes:
- This file is the daemon’s central key agreement implementation and must remain aligned with IKE group IDs exposed in configuration defaults and transform negotiation.
