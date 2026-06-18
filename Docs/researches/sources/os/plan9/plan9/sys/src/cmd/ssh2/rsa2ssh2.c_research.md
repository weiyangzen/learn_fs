# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/rsa2ssh2.c

This utility converts a Plan 9 RSA key record into an SSH2 public key line.

Key behavior:
- Reads a key record from stdin or one file.
- Extracts `ek=` and `n=` fields.
- Encodes an SSH public-key blob containing `ssh-rsa`, exponent, and modulus.
- Base64-encodes the blob and prints `ssh-rsa <blob> [user]`.

Important details:
- Uses `new_packet`, `add_string`, and `add_mp` from the SSH transport helpers to build the canonical SSH blob.
- Appends `$user` as a comment when available.
- Expects hex Plan 9 factotum-style key fields.

Filesystem relevance:
- Indirect: supports moving Plan 9 key material into SSH-compatible authorized/public key formats.
