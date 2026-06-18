# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desCBC.c

Implements single-DES CBC mode: `desCBCencrypt` and `desCBCdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Encryption XORs each full block with `s->ivec`, encrypts with `block_cipher(..., 0)`, and updates the IV to the ciphertext. Decryption saves ciphertext, decrypts with `block_cipher(..., 1)`, XORs with the previous IV, and then installs the saved ciphertext as the new IV.

Like the 3DES CBC wrapper, trailing partial blocks are processed by encrypting the IV and XORing the remaining bytes. The code warns that decryptors must receive the same buffer sizes as encryptors for compatibility.
