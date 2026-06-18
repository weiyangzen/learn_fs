# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.h

Header declaring shared RSA/DSA key parsing and binary serialization helpers used by the `rsa2*` tools.

No implementation logic; it defines the cross-file interface for `getkey`, `getdsakey`, `put4`, `putn`, `putstr`, and `putmp2`.
