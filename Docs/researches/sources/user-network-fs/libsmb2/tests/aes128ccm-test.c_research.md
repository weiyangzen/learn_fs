<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/aes128ccm-test.c -->
# sources/user-network-fs/libsmb2/tests/aes128ccm-test.c

Purpose: Standalone AES-128-CCM known-vector smoke test for libsmb2 encryption support.

Important APIs, types, and functions: Defines `test_1`, `test_2`, and `main`, calling `aes128ccm_encrypt` and `aes128ccm_decrypt` with fixed key, nonce, AAD, plaintext, tag length, and expected buffers.

Control flow: Each test copies plaintext to a work buffer, encrypts in place with tag appended, prints expected/got bytes, decrypts, and exits with code 10 on decrypt failure or plaintext mismatch.

State and persistence behavior: All state is stack/local buffers. No files or network state.

Dependencies and integration points: Depends on `lib/aes128ccm.h`; integrated through test build rules.

Risks: The code prints expected ciphertext but does not actually `memcmp` encrypted bytes against `exp`, so encryption regressions that still decrypt round-trip may pass. Exit codes are coarse.

Test signals: Directly run by the test suite when included in Automake check programs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/aes128ccm-test.c -->
