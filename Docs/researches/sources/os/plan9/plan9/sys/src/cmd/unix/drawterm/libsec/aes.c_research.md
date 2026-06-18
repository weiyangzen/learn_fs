# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/aes.c

Table-driven AES/Rijndael implementation including key setup, single-block encryption/decryption, and CBC mode entry points exposed through `libsec.h`. It includes `<u.h>`, `<libc.h>`, and `<libsec.h>`.

The file defines Rijndael T-tables (`Te0`-`Te4`, `Td0`-`Td4`) and round constants, plus static helpers `rijndaelKeySetupEnc`, `rijndaelKeySetupDec`, `rijndaelKeySetup`, `rijndaelEncrypt`, and `rijndaelDecrypt`. It supports 128-, 192-, and 256-bit keys through the standard 10/12/14 AES round counts.

Public API behavior is via `setupAESstate`, `aesCBCencrypt`, and `aesCBCdecrypt`. `setupAESstate` records the raw key, key length, expanded encryption/decryption schedules, round count, optional IV, and a setup marker. CBC encryption XORs plaintext blocks with the IV/ciphertext chain before block encryption; CBC decryption preserves ciphertext as the next IV before XORing decrypted blocks.

The implementation is portable C with conditional unaligned/little-endian load macros and optional intermediate-value KAT helpers behind preprocessor guards. It mutates the supplied buffer and AES state IV in place.
