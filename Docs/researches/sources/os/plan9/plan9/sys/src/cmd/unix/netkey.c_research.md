# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/netkey.c

Standalone legacy Plan 9 netkey challenge-response utility with embedded DES implementation.

Major pieces:
- Re-declares relevant Plan 9 auth constants and ticket structures locally.
- Implements DES block cipher tables, key setup, initial/final permutations, and encrypt/decrypt routines.
- `passtokey` derives a 7-byte DES key from a password using Plan 9's historical password-to-key algorithm.
- `netcrypt` encrypts an 8-byte challenge and formats the first four encrypted bytes as hex response.
- `main` prompts locally for a password, then repeatedly prompts for challenges and prints responses.

Notable behavior:
- Intended to be run directly on the local processor, not over a network window.
- Uses old DES-based Plan 9 authentication compatible response generation.
