# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.c

This file implements block cipher transform handling for IKE encryption.

Key responsibilities:
- Defines supported CBC transforms: 3DES, Blowfish, CAST, and AES.
- Initializes cipher-specific key schedules.
- Performs in-place encryption/decryption.
- Manages rolling IV state.
- Clones key state for exchange processing.

Important data and functions:
- `transforms[]`: table of `struct crypto_xf` entries with IDs, names, key ranges, block sizes, and function pointers.
- `des3_init`, `des3_encrypt`, `des3_decrypt`
- `blf_init`, `blf_encrypt`, `blf_decrypt`
- `cast_init`, `cast1_encrypt`, `cast1_decrypt`
- `aes_init`, `aes_encrypt`, `aes_decrypt`
- `crypto_get()`: finds transform by enum ID.
- `crypto_init()`: validates key length, allocates `keystate`, initializes IV pointers, and runs transform init.
- `crypto_init_iv()`, `crypto_update_iv()`: set and swap IV buffers.
- `crypto_encrypt()` and `crypto_decrypt()`: call transform methods and update IV state.
- `crypto_clone_keystate()`: copies state and rebinds IV pointers to the clone’s storage.

Notable behavior:
- Blowfish CBC is implemented manually using big-endian block helpers and XOR macros.
- 3DES, CAST, and AES use OpenSSL/libcrypto routines.
- AES keeps separate encrypt and decrypt key schedules.
- Debug logging can dump keys, IVs, and buffers depending on log level.

Dependencies:
- `crypto.h` for transform and key state structures.
- OpenSSL DES/CAST/AES APIs and OpenBSD Blowfish support.
- Logging framework.

Research notes:
- This is IKE payload encryption support, not kernel ESP encryption.
- Key length policy is enforced before cipher initialization.
