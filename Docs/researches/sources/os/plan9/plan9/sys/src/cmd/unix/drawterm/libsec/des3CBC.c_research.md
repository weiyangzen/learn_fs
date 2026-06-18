# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3CBC.c

Implements 3DES CBC mode: `des3CBCencrypt` and `des3CBCdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Encryption XORs each full 8-byte plaintext block with the current IV, applies `triple_block_cipher(..., DES3EDE)`, stores the ciphertext block back into the IV, and advances in place. Decryption saves the current ciphertext block, applies `triple_block_cipher(..., DES3DED)`, XORs with the previous IV, and updates the IV to the saved ciphertext.

For trailing non-8-byte data, it encrypts the IV and XORs the remaining bytes. Comments state that decryptors must be fed buffers of the same size as encryptors because of this partial-block convention.
