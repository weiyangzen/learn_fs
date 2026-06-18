# sources/user-network-fs/libsmb2/lib/aes128ccm.h

Purpose: Declares the small public/internal AES-128 CCM interface used by libsmb2 C files.

Important APIs/types/functions: `aes128ccm_encrypt` and `aes128ccm_decrypt` take raw byte pointers for key, nonce, additional authenticated data, payload, MAC, and their lengths. The encrypt function has no return value; decrypt returns the result of comparing the calculated tag to the supplied tag.

Control flow: The header contains declarations only; callers are responsible for sequencing encryption/decryption and checking decrypt return values.

State/persistence: No types or state are declared. The underlying implementation mutates payload and tag buffers, which is not visible from the header comments.

Dependencies/integration: The header relies on `size_t` being declared before inclusion; it does not include `<stddef.h>`. It is included by `tests/aes128ccm-test.c` and expected to pair with `aes128ccm.c`.

Risks: Lack of include guard and missing `stddef.h` make it fragile when included in multiple or minimal translation units. The API does not document in-place mutation, accepted nonce/tag sizes, or that decrypt returns zero on success and nonzero on failure.

Test signals: Compile smoke tests should include this header alone after `<stddef.h>`, and negative compile tests or static analysis should flag duplicate inclusion if the header is expanded in generated amalgamations.
