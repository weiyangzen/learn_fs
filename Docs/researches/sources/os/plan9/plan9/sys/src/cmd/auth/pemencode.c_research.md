# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/pemencode.c

Reads binary input from a file or stdin, base64 encodes it, and emits a PEM block with the supplied tag. Output lines are wrapped at 64 characters.

The usage string mistakenly says `auth/pemdecode`, but behavior is PEM encoding.
