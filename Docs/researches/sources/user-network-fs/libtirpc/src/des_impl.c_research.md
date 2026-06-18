## sources/user-network-fs/libtirpc/src/des_impl.c

Purpose: Contains the table-driven software DES implementation used by `des_crypt.c`.

Important APIs and control flow: Large static lookup tables `des_SPtrans` and `des_skb` implement S-box/permutation work. `des_set_key` converts the 8-byte key into a 32-word key schedule using DES key permutations and the `shifts2` rotation plan. `des_encrypt` applies initial permutation, 16 Feistel rounds using the schedule in forward or reverse order, then final permutation. `_des_crypt` prepares the schedule, walks the caller buffer in 8-byte blocks, applies CBC XOR chaining when requested, encrypts or decrypts in place, updates the IV to the final ciphertext/plaintext dependency, clears temporaries and the schedule, and returns success.

State and persistence: Static tables are read-only. The buffer and `desparams->des_ivec` are mutable caller state.

Dependencies and integration: Called only by `common_crypt`. Uses DES layout macros and `struct desparams`.

Risks and test signals: Table correctness, endian conversion macros, and 32-bit masking on 64-bit `unsigned long` are critical. Tests should use standard DES vectors for ECB/CBC, multi-block IV chaining, decrypt inverse, and sanitizer checks for unaligned buffers.
