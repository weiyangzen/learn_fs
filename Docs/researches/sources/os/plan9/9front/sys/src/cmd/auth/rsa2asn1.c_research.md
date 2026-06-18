# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2asn1.c

RSA key converter to ASN.1 DER.

Key responsibilities:
- Reads a Plan 9 RSA key.
- With `-a`, emits private PKCS#1 DER.
- Without `-a`, emits public PKCS#1 DER by default or SPKI DER with `-f spki`.
- Writes binary DER to stdout.

Dependencies:
- Uses `getrsakey`, `asn1encodeRSApriv`, `asn1encodeRSApub`, and `asn1encodeRSApubSPKI`.
