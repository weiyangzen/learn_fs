# File Research: sources/os/plan9/9front/sys/src/cmd/auth/asn1dump.c

ASN.1/X.509 dump utility.

Key responsibilities:
- Reads ASN.1 DER input from a file or stdin.
- Installs formatting hooks for multiprecision integers and hex/base encodings.
- Calls `asn1dump()` and `X509dump()` on the full input buffer.

Dependencies:
- Uses libsec ASN.1/X.509 dump routines.

Research notes:
- This is a diagnostic utility; it does not validate command-specific object types.
