# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipher3des.c

SSH1 3DES cipher adapter.

Key responsibilities:
- Initializes three DES states from the 32-byte SSH1 session key.
- Implements encrypt-decrypt-encrypt 3DES CBC and reverse decrypt path.
- Exports `Cipher cipher3des`.

Risks/quirks:
- Uses first 24 bytes of `sesskey`.
- Separate encryption/decryption states are initialized with same key material and implicit IV behavior from libsec.
