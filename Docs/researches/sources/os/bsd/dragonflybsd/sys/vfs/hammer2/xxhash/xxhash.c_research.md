# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/xxhash/xxhash.c

Vendored xxHash 0.6.0 implementation adapted for DragonFly kernel builds and namespaced for HAMMER2.

Key responsibilities:
- Implements one-shot `XXH32()` and `XXH64()` hash functions.
- Implements streaming state reset, update, and digest for 32-bit and 64-bit hashes.
- Implements optional userland dynamic state allocation/free, excluded for `_KERNEL` builds.
- Implements canonical big-endian conversion to/from 32-bit and 64-bit hash digests.
- Provides endian-independent reads, byte swapping, alignment-aware fast paths, avalanche finalization, and architecture/compiler tuning macros.

Important implementation details:
- Includes `<sys/types.h>` and `<sys/systm.h>` in kernel builds; userland builds use libc allocation/string headers.
- `XXH_STATIC_LINKING_ONLY` is defined before including the header so internal state layouts are visible.
- Public symbols are transformed by `XXH_NAMESPACE h2_` from the header.
- Memory reads use one of three strategies depending on `XXH_FORCE_MEMORY_ACCESS`: memcpy-safe, packed union, or direct unaligned access.
- Hashes are little-endian canonical internally unless `XXH_FORCE_NATIVE_FORMAT` is enabled.
- Streaming updates buffer incomplete 16-byte or 32-byte stripes in state and process full stripes through four accumulators.
- Canonical representations are explicitly big-endian for persistent/cross-platform comparison.

Dependencies:
- Depends on `xxhash.h` for API types, namespace macros, and static state layouts.
- In kernel mode, depends on DragonFly kernel `memcpy`, `memset`, and basic integer types.

Notable risks:
- Null input pointers are invalid unless `XXH_ACCEPT_NULL_INPUT_POINTER` is enabled; callers must not pass null with nonzero lengths.
- Forced direct unaligned access can violate C aliasing/alignment assumptions on some targets if selected incorrectly.
- Cross-platform persistent hash compatibility depends on leaving endian behavior and canonical conversion semantics unchanged.
- Dynamic create/free APIs are not compiled in `_KERNEL` mode; kernel callers must use stack/static state where needed.
