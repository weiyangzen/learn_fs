# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/aescbc.c

Standalone AES-CBC file encrypt/decrypt utility used by secstore workflows.

Key responsibilities:
- Reads password from console, fd 3 (`-i`), or NVRAM config (`-n`).
- Derives AES key from SHA1 label plus passphrase, then derives HMAC key with MD5 of AES key.
- Encrypts with header `AES CBC SHA1  2\n`, random IV, random initial plaintext block, AES-CBC data, and HMAC-SHA1 trailer.
- Decrypts v2 format, verifies HMAC, and writes plaintext.
- Includes compatibility decryption path for older secstore format with sentinel block.
- Supports `-e` encryption; default path is decryption despite usage text mentioning `-d`.

Dependencies:
- Uses libsec AES-CBC, SHA1, HMAC-SHA1, MD5, NVRAM, Biobuf, and console prompting.

Notable risks:
- Legacy compatibility path has weaker authentication semantics than the v2 HMAC path.
