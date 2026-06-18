# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsatest.c

Standalone RSA test and timing program. It includes `os.h`, `<mp.h>`, `<libsec.h>`, and `<bio.h>`.

`main` generates a 1024-bit RSA key, encrypts a fixed hex plaintext, times ten CRT decryptions versus ten raw `mpexp` private exponentiations, compares results, then enters an interactive loop reading lines, converting them to little-endian `mpint`s, encrypting/decrypting, printing intermediate values, and writing recovered bytes.

This file exercises RSA behavior and performance but is not included in the static library object list.
