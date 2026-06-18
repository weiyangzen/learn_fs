# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsagen.c

Generates a new RSA private key line for factotum. Options set bit length (`-b`, default 1024) and extra attrs (`-t`). It loops until the modulus has exactly the requested bit length.

Outputs `proto=rsa`, optional tag attrs, `size`, public exponent, private exponent, modulus, primes, and CRT fields.
