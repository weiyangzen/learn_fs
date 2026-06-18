# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/keyfmt.c

Defines `%K` formatting for DES keys. It converts the internal 7-byte DES key representation into 8 parity-cleared bytes and prints each byte in three-digit octal.

Used by tools such as `printnetkey` for operator-readable key display.
