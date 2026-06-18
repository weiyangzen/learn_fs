# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egtest.c

Small ElGamal decryption test program with `main`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The test constructs a fixed private key with small values (`p=2357`, `alpha=2`, public key `1185`, secret `1751`), expected message `2035`, and a packed ciphertext made from fixed `gamma=1430` and `delta=697`.

It calls `egdecrypt` and prints an error if the recovered message differs from the expected value. This is a diagnostic/test file, not part of the static `libsec.a` object list in the Makefile.
