# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/asn12dsa.c

Converts ASN.1 DSA private keys to Plan 9 factotum key text.

Key points:
- Reads all input from a file or stdin.
- Parses with `asn1toDSApriv`.
- Prints a `key proto=dsa` line with optional tag, public parameters, public key, and private secret.

Dependencies:
- Uses `mp`, `libsec`, and `%B` multiprecision formatting.

Notable behavior:
- Optional `-t` prepends arbitrary key attributes.
