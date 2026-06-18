# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2ssh.c

Converts an RSA key to old SSH public-key text format: bit length, exponent, modulus. It accepts an optional input file and requires only public key fields.

Uses `%B` mpint formatting with precision limits for exponent/modulus.
