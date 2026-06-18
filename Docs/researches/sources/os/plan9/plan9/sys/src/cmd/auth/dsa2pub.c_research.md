# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2pub.c

Extracts a public DSA factotum key.

Key points:
- Reads a DSA key using `getdsakey`.
- Preserves parsed public attributes.
- Prints `key ... p= q= alpha= key=` without the private secret.

Dependencies:
- Uses helper definitions from `rsa2any.h`, multiprecision formatting, and auth attribute formatting.

Notable behavior:
- Accepts zero or one input file.
