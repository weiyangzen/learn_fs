# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphertwiddle.c

Debug cipher for SSH1.

Key responsibilities:
- Prints the session key.
- XORs every byte with `0xFF` for both encrypt and decrypt.
- Exports `Cipher ciphertwiddle`.

Use:
- Debugging only.

Risks/quirks:
- Not cryptographically meaningful and leaks key material to stderr.
