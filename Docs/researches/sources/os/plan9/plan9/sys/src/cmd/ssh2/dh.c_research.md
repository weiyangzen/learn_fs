# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/dh.c

This file implements SSH2 Diffie-Hellman key exchange and RSA/DSA public-key algorithm hooks for Plan 9 `netssh`.

Key behavior:
- Defines Oakley group1 and MODP group14 primes, initializes mp arithmetic, and loads RSA/DSA host keys from environment variables, `rsakey`/`dsskey`, or `/mnt/factotum/ctl`.
- Implements RSA key-serialization, PKCS#1/SHA1 signing locally or through factotum, and factotum-backed RSA verification.
- Implements DSA key serialization/signing; DSA verification is a stub returning failure.
- Implements server-side DH reply generation for group1/group14 and client-side group1 initiation/reply handling.
- Derives SSH IVs, encryption keys, and integrity keys from `K`, exchange hash `H`, and session id.

Important details:
- `VERIFYKEYS` is explicitly undefined and `netssh` defaults to skipping host-key verification, reflecting unfinished verification support.
- RSA private signing can use local `!dk=` material or `/mnt/factotum/rpc`.
- `dh_client14*` support is incomplete: it sends group14 init but does not process the reply.
- Key generation fills 40 bytes per direction/key class by chaining SHA1 as RFC 4253 requires.

Filesystem relevance:
- Indirect: cryptographic transport layer for `/net/ssh`, the synthetic SSH filesystem served by `netssh`.
