# sources/user-network-fs/libsmb2/lib/aes_apple.h

Purpose: Declares the Apple CommonCrypto AES-128 ECB encrypt backend when building on Apple platforms.

Important APIs/types/functions: Under `__APPLE__`, exports `AES128_ECB_encrypt_apple(const uint8_t *input, const uint8_t *key, uint8_t *output)`. It includes `config.h` and `<stdint.h>` when available.

Control flow: Preprocessor-only header with an include guard. Non-Apple builds see no function declaration.

State/persistence: No state or allocation behavior is exposed.

Dependencies/integration: Included by `aes.c` and `aes_apple.c`; `aes.c` selects this backend before falling back to the reference implementation. CommonCrypto itself is included only by the C file.

Risks: The function returns `void`, so backend errors cannot be propagated. The prototype is only present on Apple, which is intentional but means generic code should call `AES128_ECB_encrypt`, not this backend directly.

Test signals: Build matrix should include Apple and non-Apple compilation to ensure conditional declaration paths stay valid. AES known-answer tests should execute through the top-level `AES128_ECB_encrypt` dispatcher.
