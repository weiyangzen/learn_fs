# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3ECB.c

Implements 3DES ECB mode: `des3ECBencrypt` and `des3ECBdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Full 8-byte blocks are transformed in place with `triple_block_cipher`, using EDE for encryption and DED for decryption. For trailing bytes, the code initializes a temporary block to bytes `0..7`, encrypts it with EDE, and XORs the remaining input bytes with that result.

The file comments explicitly call the partial-block behavior dangerous but retained for compatibility with older cryptlib behavior.
