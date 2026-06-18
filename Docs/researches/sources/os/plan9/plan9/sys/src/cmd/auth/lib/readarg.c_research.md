# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readarg.c

Reads a NUL-terminated argument from a file descriptor into a fixed buffer. It zeroes the destination first, stores up to `len-1` bytes, and succeeds once `\0` is read.

Used by service protocols that exchange NUL-terminated text fields over stdin/stdout.
