# File Research: sources/os/bsd/netbsd-src/sys/sys/sha1.h

Read completely: 38 lines.

This header declares SHA-1 constants, `SHA1_CTX`, and core functions `SHA1Transform`, `SHA1Init`, `SHA1Update`, and `SHA1Final`. Userland additionally gets `SHA1End`, `SHA1FileChunk`, `SHA1File`, and `SHA1Data`.

Risks: SHA-1 is cryptographically weak for collision resistance. The header is ABI-only, but new security-sensitive code should not choose SHA-1 for collision-resistant use.
