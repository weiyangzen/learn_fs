# sources/user-network-fs/libsmb2/lib/aes_reference.c

Purpose: Provides a tiny-AES-derived portable AES-128 implementation for ECB by default and CBC when `CBC` is enabled before including `aes_reference.h`.

Important APIs/functions: `AES128_ECB_encrypt_reference` and `AES128_ECB_decrypt_reference` operate on one 16-byte block. Optional `AES128_CBC_encrypt_buffer_reference` and `AES128_CBC_decrypt_buffer_reference` process buffers with zero padding. Internal core consists of S-box tables, `smb2_KeyExpansion`, `smb2_Cipher`, `smb2_InvCipher`, row/column transforms, and block copy/XOR helpers.

Control flow: Public ECB functions copy input to output, expand the 128-bit key into 176 round-key bytes, then run AES rounds. CBC encrypt XORs each input block with the IV/previous ciphertext before encryption and pads the final partial block with zeros; decrypt reverses the block transform and XORs with IV/previous ciphertext.

State/persistence: No global mutable state. Tables are static const. Round keys live on the stack. CBC mutates the IV pointer locally and writes to caller-provided output.

Dependencies/integration: Included in build files and selected by `aes.c` on non-Apple systems. `smb2-signing.c` defines `CBC 1` before including the header to enable CBC declarations for CMAC-related code; AES-CCM uses the ECB dispatcher.

Risks: This is not constant-time and uses table lookups, so it is not hardened against side-channel attacks. CBC zero padding is not a general authenticated padding scheme. Optional compile-time macros can change exported symbols; build coverage must exercise the intended macro combinations. There is no runtime error reporting.

Test signals: Validate ECB against NIST SP 800-38A vectors documented in the file, CBC round trips with partial blocks, and cross-backend equality with Apple CommonCrypto. Run AES-CCM and SMB2 signing tests because they transitively depend on this implementation.
