# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmactest.c

Small HMAC-MD5 test program. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The test uses key `"Jefe"` and data `"what do ya want for nothing?"`, computes `hmac_md5`, prints the hexadecimal digest, then prints the expected digest `750c783e6ab0b503eaa86e310a5db738`.

This file is a diagnostic vector check and is not listed in `libsec/Makefile`’s `OFILES`.
