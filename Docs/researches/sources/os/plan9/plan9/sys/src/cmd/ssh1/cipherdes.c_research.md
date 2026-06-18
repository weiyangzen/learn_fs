# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherdes.c

SSH1 DES cipher adapter.

Key responsibilities:
- Initializes DES CBC state from session key.
- Provides encrypt/decrypt callbacks.
- Exports `Cipher cipherdes`.

Risks/quirks:
- DES is legacy/weak; included for SSH1 compatibility.
