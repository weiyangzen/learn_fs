# File Research: sources/virtualization/qemu/block/crypto.h

Defines crypto block option names and `QemuOptDesc` helper macros for QCOW and LUKS encryption options. LUKS options include key secret, cipher algorithm/mode, IV generator and hash, hash algorithm, PBKDF iteration time, detached-header flag, keyslot, state, old secret, and new secret.

The header also declares the three QDict-to-QAPI parser helpers: `block_crypto_create_opts_init()`, `block_crypto_amend_opts_init()`, and `block_crypto_open_opts_init()`.
