# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/asn12rsa.c

Converts ASN.1 RSA private keys to Plan 9 factotum key text.

Key points:
- Reads all input from a file or default `#d/0`.
- Parses with `asn1toRSApriv`.
- Prints `key proto=rsa` with size, public exponent, private exponent, modulus, primes, CRT exponents, and coefficient.
- Supports optional `-t` tag attributes.

Dependencies:
- Uses `mp` and `libsec`.

Notable behavior:
- Private fields are printed with `!` attribute names for factotum secrecy convention.
