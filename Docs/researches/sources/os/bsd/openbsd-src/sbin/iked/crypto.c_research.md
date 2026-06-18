# File Research: sources/os/bsd/openbsd-src/sbin/iked/crypto.c

`crypto.c` wraps OpenSSL primitives behind iked’s negotiated crypto interfaces. It implements PRF/integrity hashes, encryption ciphers, AEAD handling, and AUTH signing/verification for RSA, ECDSA, RFC7427 generic signatures, and shared-key MICs.

`hash_new()` supports HMAC-MD5, HMAC-SHA1, HMAC-SHA2 PRFs, truncated HMAC integrity algorithms, and AEAD integrity marker entries for AES-GCM. `cipher_new()` supports 3DES-CBC, AES-CBC, and AES-GCM variants, including salt+IV nonce construction for AEAD.

The DSA layer handles HMAC authentication, legacy RSA SHA1 signatures, fixed ECDSA SHA2 methods, and RFC7427 signature-scheme OID prefixes. ECDSA signatures are converted between IKEv2 concat `r|s` format and OpenSSL DER `ECDSA_SIG` format.

Security-relevant details: padding is disabled for IKE encryption, GCM tags are managed explicitly, RFC7427 verification selects the digest based on the encoded OID prefix, and RSA-PSS can be forced through the global `force_rsa_pss`. HMAC verify uses direct `memcmp`, so constant-time comparison is not provided here.
