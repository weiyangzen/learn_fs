# File Research: sources/os/bsd/openbsd-src/sbin/iked/dh.c

`dh.c` implements iked’s Diffie-Hellman/key-exchange group abstraction. It supports MODP groups, ECP groups, Curve25519, and a private-use hybrid SNTRUP761+X25519 group.

The `ike_groups[]` table defines supported IKE DH group IDs, types, bit sizes, MODP primes/generators, ECP OpenSSL NIDs, Curve25519, and SNTRUP761X25519 group 1035. `group_get()` selects function pointers for group-specific init, exchange, and shared-secret creation.

MODP uses OpenSSL DH with fixed RFC prime/generator values. ECP generates an EC key, encodes public exchange as raw `x|y`, validates peer public keys through `EC_KEY_check_key()`, and derives the x-coordinate shared secret per RFC5903. Curve25519 uses `crypto_scalarmult_curve25519()`.

The hybrid KEM path delays setup until exchange creation. Initiators send SNTRUP761 public key plus X25519 public key; responders encapsulate to the KEM public key and send ciphertext plus X25519 public key. Shared output is SHA512 over KEM key material and X25519 shared secret.

Security-relevant details: group teardown zeroes Curve25519 and KEM private storage, EC temporary BIGNUMs and points are cleared, exchange sizes are strictly checked, and MODP/ECP outputs are zero-padded to fixed protocol lengths.
