
## sources/storage-engines/wiredtiger/ext/encryptors/rotn/rotn_encrypt.c

Purpose: demonstration/test encryptor implementing ROT-N without a secret key and a Vigenere-like byte shift when `secretkey` is configured. The file explicitly warns that it provides no real security.

Important APIs/types/functions: `ROTN_ENCRYPTOR` stores `rot_N`, copied key strings, forward/backward shift arrays, and `force_error`. Constants define a 4-byte checksum and 16-byte IV expansion. `rotn_encrypt` writes dummy checksum and IV, copies plaintext, then rotates alphabetic characters or shifts all bytes. `rotn_decrypt` strips the header and reverses the transform, optionally returning `-1000` for testing. `rotn_sizing` reports 20 bytes of expansion. `rotn_customize` parses `keyid` and alphabetic `secretkey`, builds shift arrays, and sets `rot_N`. `rotn_configure` handles `rotn_force_error`.

State and persistence: encrypted blocks persist `CCCC` checksum, `IIII...` IV, and transformed data. Customized encryptors own allocated key/shift arrays and free them on terminate. Risks: checksum and IV are constants, keyid uses `atoi` so nonnumeric prefixes can be accepted as zero, decrypt can underflow if input is shorter than the fixed header, and encrypt reports `dst_len` rather than the actual required length if overallocated. Tests should cover ROT and Vigenere round trips, invalid secret characters, forced decrypt errors, short ciphertext, sizing, and cleanup after customize failures.
