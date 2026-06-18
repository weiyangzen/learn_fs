# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/netcheck.c

Securenet challenge-response helper routines.

Key responsibilities:
- Computes DES key verification checksum.
- Computes hex challenge response by encrypting ASCII challenge text.
- Converts hex answers to decimal-mode answers for older Securenet modes.
- Checks responses against smart-token format, hex format, and decimal format.
- Implements `smartcheck` checksum-style response validation.

Dependencies:
- Uses DES `encrypt`, shared `error`, and Plan 9 auth key constants.

Notable risks:
- Mutates the response buffer while normalizing uppercase and stripping newline.
