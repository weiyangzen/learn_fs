# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherblowfish.c

SSH1 Blowfish cipher adapter.

Key responsibilities:
- Initializes Blowfish CBC state from full SSH1 session key.
- Provides encrypt/decrypt callbacks.
- Exports `Cipher cipherblowfish`.

Risks/quirks:
- Uses libsec `BFstate` with nil IV.
