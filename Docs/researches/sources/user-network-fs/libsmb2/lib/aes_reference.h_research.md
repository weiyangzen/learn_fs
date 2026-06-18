# sources/user-network-fs/libsmb2/lib/aes_reference.h

Purpose: Configures and declares the portable reference AES-128 backend.

Important APIs/types/functions: Defaults `CBC` to 0 and `ECB` to 1 if not provided. Declares ECB encrypt/decrypt functions when `ECB` is enabled and CBC buffer encrypt/decrypt functions when `CBC` is enabled.

Control flow: Header behavior is controlled entirely by preprocessor macros, allowing a translation unit such as `smb2-signing.c` to enable CBC before inclusion.

State/persistence: No state. Exposes raw block/buffer APIs that require caller-managed buffers, IVs, and padding expectations.

Dependencies/integration: Included by `aes_reference.c`, `aes.c`, and code that needs optional CBC prototypes. Uses `config.h` and `<stdint.h>` conditionally.

Risks: Macro-controlled declarations can diverge between translation units if `CBC`/`ECB` settings differ unexpectedly. The trailing guard comment says `_AES_H_`, which is inaccurate but harmless. APIs return `void`, so misuse is only observable through downstream cryptographic mismatches.

Test signals: Compile with default macros and with `CBC=1`; run ECB/CBC known-answer tests and any consumers that call the top-level `AES128_ECB_encrypt` dispatcher.
