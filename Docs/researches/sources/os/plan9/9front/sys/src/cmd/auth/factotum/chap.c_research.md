# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/chap.c

Factotum protocol module for CHAP, MSCHAP, MSCHAPv2, NTLM, and NTLMv2.

Key responsibilities:
- Implements shared client/server state machines for CHAP-family mechanisms.
- Client mode generates CHAP MD5, MSCHAP, MSCHAPv2, NTLM, or NTLMv2 replies from a password key.
- Server mode obtains challenge material from authsrv, collects user/domain/response fields, and relays protocol-specific replies to authsrv.
- Computes NT hash, LM hash, MSCHAP response blocks, NTLMv2 blob, and MSCHAPv2 peer challenge response.
- Produces MPPE/session secret material for MSCHAP/MSCHAPv2 where available.
- Produces `AuthInfo` after successful server-side validation.

Dependencies:
- Uses factotum key lookup, libsec MD4/MD5/SHA1/HMAC/DES helpers, authsrv ticket/authenticator routines, and protocol reply structures.

Notable risks:
- Client modes do not authenticate the server except for derived secret semantics.
- This file contains compatibility cryptography for legacy Microsoft protocols.
