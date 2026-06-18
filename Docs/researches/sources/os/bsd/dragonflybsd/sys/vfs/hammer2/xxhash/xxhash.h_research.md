# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.h

Vendored xxHash public/static-linking header with DragonFly-specific symbol namespacing.

Key responsibilities:
- Defines `XXH_NAMESPACE h2_` so all public xxHash symbols are compiled/exported as HAMMER2-private names.
- Declares xxHash version constants and `XXH_versionNumber()`.
- Declares one-shot 32-bit and 64-bit hash APIs.
- Declares streaming state opaque types, create/free/reset/update/digest APIs, and canonical digest conversion APIs.
- Defines `XXH_PUBLIC_API` behavior for normal vs private/static inclusion.
- Under `XXH_STATIC_LINKING_ONLY`, exposes internal `XXH32_state_s` and `XXH64_state_s` layouts.

Important implementation details:
- Skips `<stddef.h>` when `_KERNEL` is defined, relying on kernel-provided `size_t`.
- Namespace macros rewrite `XXH32`, `XXH64`, version, state allocation, reset, update, digest, and related public names.
- Canonical digest structs are byte arrays sized to 4 and 8 bytes.
- Static state layouts contain total length, seed, four accumulators, aligned scratch buffer, and scratch size.

Dependencies:
- Used by `xxhash.c` and by HAMMER2 wrapper `hammer2_xxhash.h`.
- Depends on callers including it consistently with the same namespace/static-linking settings as the compiled implementation.

Notable risks:
- Changing namespace macros can create kernel symbol collisions with other xxHash copies.
- Exposed static-linking state layouts are explicitly not stable upstream API; code depending on them is tied to this vendored version.
- Header/API version is old (`0.6.0`); replacing it requires verifying HAMMER2 hash compatibility and kernel build assumptions.
