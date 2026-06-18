# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.h

Shared declarations for RSA conversion tools.

Key contents:
- Declares `getrsakey`.
- Declares binary packing helpers: `put4`, `putmp2`, `putn`, and `putstr`.

Role:
- Small common interface used by `rsa2asn1`, `rsa2csr`, `rsa2jwk`, `rsa2pub`, `rsa2ssh`, `rsa2x509`, and `rsafill`.
