# sources/test-tools/fio/crc/xxhash.h

Purpose: Declares the embedded xxHash 32-bit API and streaming state layout.

Important APIs/types: Defines `struct XXH_state32_t`, `XXH_errorcode`, one-shot `XXH32()`, heap streaming API `XXH32_init/update/digest`, caller-allocated state API `XXH32_sizeofState()` and `XXH32_resetState()`, `XXH32_stateSpace_t`, and deprecated macro aliases.

Control flow: Callers either hash a single buffer with `XXH32()` or initialize state, feed packets with `XXH32_update()`, optionally sample `XXH32_intermediateDigest()`, and finish/free with `XXH32_digest()`.

State/persistence: The state structure is public and can be stack allocated, but callers must preserve its contents between updates. `XXH32_digest()` frees heap states and must not be used on stack state unless the caller intentionally allocated compatible heap memory.

Dependencies/integration: Includes `<inttypes.h>` and supports C++ linkage. Used by local fio checksum consumers.

Risks: Public exposure of the internal state makes ABI drift risky. `XXH32_SIZEOFSTATE` must remain large enough; the implementation asserts this at compile time. Documentation says some lengths are limited by `int` although the one-shot prototype uses `uint32_t`.

Test signals: Compile tests should validate both heap and stack state modes; runtime tests should compare intermediate digest preservation with continued updates.
