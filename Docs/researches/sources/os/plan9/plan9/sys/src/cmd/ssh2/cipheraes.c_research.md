# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipheraes.c

SSH2 AES-CBC cipher adapters.

Key responsibilities:
- Implements shared AES initialization for 128/192/256-bit keys.
- Provides CBC encrypt/decrypt callbacks.
- Exports `aes128-cbc`, `aes192-cbc`, and `aes256-cbc` `Cipher` objects.

Important details:
- Uses a global `QLock aeslock` around AES setup/encrypt/decrypt.
- Selects key/IV direction from `dir`.
- Guards encrypt/decrypt with checks on `AESstate.setup` and rounds.

Risks/quirks:
- If AES state validation fails, encrypt/decrypt silently returns without transforming data.
- Global lock serializes all AES operations.
