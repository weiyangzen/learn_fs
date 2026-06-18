# File Research: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.h

`chap_ms.h` declares the MS-CHAP/MS-CHAPv2 helper API and protocol sizes. It defines challenge, hash, master-key, MSK key, MSK padding, total MSK, and maximum NT password sizes.

The header exports functions for NT response generation, authenticator response generation, NT password hashing, challenge hashing, asymmetric key derivation, master-key derivation, RADIUS key decoding, and MSK construction.

This file is intentionally narrow: it exposes cryptographic helper routines to EAP/RADIUS code without defining daemon state.
