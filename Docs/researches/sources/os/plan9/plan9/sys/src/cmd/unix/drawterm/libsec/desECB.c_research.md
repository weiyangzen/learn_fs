# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desECB.c

Implements single-DES ECB mode: `desECBencrypt` and `desECBdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Full 8-byte blocks are transformed in place using `block_cipher`, with direction `0` for encryption and `1` for decryption. Partial trailing data is XORed with an encrypted deterministic temporary block containing bytes `0..7`.

The file’s comment notes uncertainty and risk around the non-multiple-of-8 behavior, retained only to match older cryptlib compatibility.
