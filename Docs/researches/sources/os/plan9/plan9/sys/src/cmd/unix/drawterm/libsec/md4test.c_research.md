# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4test.c

MD4 test program. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The file defines standard MD4 test input strings, from the empty string through the long numeric sequence. `main` hashes each string with `md4`, then prints each digest byte in hex.

It is a standalone diagnostic program and is not included in the `libsec.a` object list.
