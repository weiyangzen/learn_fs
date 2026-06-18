# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsafill.c

Reads an RSA private key, regenerates/ensures CRT components through shared `getkey`, and prints a complete factotum RSA key line containing public and private fields.

Useful for repairing keys missing `!kp`, `!kq`, or `!c2`.
