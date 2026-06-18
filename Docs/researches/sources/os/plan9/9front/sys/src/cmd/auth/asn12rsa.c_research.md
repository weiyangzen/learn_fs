# File Research: sources/os/plan9/9front/sys/src/cmd/auth/asn12rsa.c

ASN.1 RSA key converter to Plan 9 factotum key syntax.

Key responsibilities:
- Reads ASN.1 DER data from a file or stdin.
- Attempts to parse an RSA private key first, then an RSA public key.
- Prints a factotum `key proto=rsa ...` line with optional tag fields.
- Emits private components with `!` prefixes for secret attributes.

Dependencies:
- Uses libsec ASN.1/RSA parsing and multiprecision formatting.

Research notes:
- Entire input is slurped into memory before parsing.
