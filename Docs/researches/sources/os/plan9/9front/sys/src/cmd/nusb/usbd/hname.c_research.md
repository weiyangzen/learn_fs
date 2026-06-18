# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hname.c

## Role

Generates compact stable USB hardware-name prefixes.

## Main Behavior

`hname` SHA1-hashes the caller-provided identity string, derives a 20-bit value from the first three digest bytes, and overwrites the input buffer with a five-hex-digit name.

`assignhname` in `usbd.c` uses this as the base name and appends collision suffixes when needed.
