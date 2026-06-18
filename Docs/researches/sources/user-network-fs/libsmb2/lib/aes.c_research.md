# sources/user-network-fs/libsmb2/lib/aes.c

## Purpose
`aes.c` provides the common `AES128_ECB_encrypt()` wrapper used by libsmb2 crypto code.

## Important APIs, Types, and Functions
It includes `aes.h` and then selects `aes_apple.h` on Apple platforms or `aes_reference.h` otherwise. The only function, `AES128_ECB_encrypt(uint8_t *input, const uint8_t *key, uint8_t *output)`, delegates to `AES128_ECB_encrypt_apple()` or `AES128_ECB_encrypt_reference()`.

## Control Flow
At compile time, `#ifdef __APPLE__` selects the backend include and delegate call. Runtime control flow is a single direct call to the selected backend.

## State and Persistence Behavior
No state is retained. The function reads a 16-byte block and key according to backend expectations and writes the encrypted block to `output`.

## Dependencies and Integration Points
It integrates with SMB signing/sealing or related crypto helpers that need AES-128 ECB. It depends on backend headers/sources being present in the build lists; CMake includes both Apple and reference sources in normal builds but ESP/PS2 branches omit `aes_apple.c`.

## Risks and Edge Cases
There is no argument validation for NULL pointers or overlapping buffers. ECB is only a primitive here; higher-level code must use it safely within correct modes. Apple backend availability must match build branch.

## Test Signals
Run AES-128 ECB known-answer tests on Apple and non-Apple builds, test repeated calls, and verify higher-level SMB3 signing/sealing tests that depend on AES.
