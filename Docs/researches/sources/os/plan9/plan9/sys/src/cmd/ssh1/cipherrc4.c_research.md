# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherrc4.c

SSH1 RC4 cipher adapter.

Key responsibilities:
- Splits session key into client-to-server and server-to-client RC4 keys.
- Direction depends on whether initialized as server or client.
- Provides symmetric stream encrypt/decrypt callbacks.
- Exports `Cipher cipherrc4`.

Risks/quirks:
- RC4 is legacy/weak but present for SSH1 compatibility.
