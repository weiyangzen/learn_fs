# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/pk.c

## Purpose
Implements SRA public-key helper routines: key generation, shared-key derivation, and DES-CBC hex encoding/decoding.

## Main Interfaces
Exports `genkeys`, `common_key`, `pk_encode`, and `pk_decode`.

## Control Flow And State
`genkeys` creates a random secret exponent from `arc4random`, reduces it modulo a fixed 192-bit modulus, computes public key `PROOT^secret mod modulus`, converts secret/public BIGNUMs to fixed-width hex strings, and zero-pads them via `adjust`.

`common_key` parses local secret, peer public key, and fixed modulus, computes the Diffie-Hellman shared value, extracts a middle 64-bit DES key and upper 128-bit IDEA key, and sets DES odd parity.

`pk_encode` DES-CBC encrypts a NUL-padded string with zero IV, rounds length to an 8-byte boundary, and emits uppercase hex. `pk_decode` parses hex pairs, DES-CBC decrypts with zero IV, and NUL-terminates the output.

## Dependencies
Uses OpenSSL BIGNUM APIs, DES APIs, `arc4random`, and constants/types from `pk.h`.

## Risks And Notes
The fixed 192-bit modulus and DES-CBC wrapping are legacy and weak by modern standards. `pk_encode` and `pk_decode` use 256-byte local buffers and rely on callers passing bounded strings. BIGNUM hex strings returned by `BN_bn2hex` are not freed in `genkeys`, causing small leaks on key generation.
