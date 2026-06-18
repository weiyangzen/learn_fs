# File Research: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.c

`chap_ms.c` implements MS-CHAP/MS-CHAPv2 and MPPE key derivation helpers used by EAP authentication. It follows RFC2433, RFC2759, and RFC3079, using OpenSSL MD4, MD5, SHA1, and DES APIs.

Core functions generate NT password hashes, challenge hashes, NT responses, authenticator responses, master keys, asymmetric send/receive start keys, 64-byte MSK material, and decrypted RADIUS MPPE keys. Internal DES helpers expand 56-bit key material to DES parity form and encrypt the challenge in three blocks.

The file is protocol glue rather than daemon orchestration. It does not allocate persistent objects, but it relies on exact fixed-size protocol buffers and legacy crypto primitives required by MS-CHAPv2 compatibility.

Security-relevant details: it implements known-weak legacy MS-CHAPv2 primitives but only as required protocol support. Callers must provide correctly sized output buffers; most functions assume fixed protocol sizes rather than doing dynamic bounds checks.
