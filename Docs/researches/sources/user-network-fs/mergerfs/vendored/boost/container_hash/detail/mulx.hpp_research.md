# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/mulx.hpp

Purpose: Provides `boost::hash_detail::mulx`, a 64-bit multiplication helper that returns the xor of the low and high halves of a 128-bit product for hash mixing.

Important APIs, types, and functions: Single exported helper `mulx(std::uint64_t, std::uint64_t)`. Implementations use MSVC `_umul128` on x64, `__umulh` on MSVC ARM64, `__uint128_t` where available, or a portable 32-bit limb multiplication fallback.

Control flow: Preprocessor selects one implementation at compile time. Runtime flow is a straight multiplication and fold of high/low product bits.

State and persistence behavior: Stateless pure arithmetic helper.

Dependencies and integration points: Used by `hash_range.hpp` for 64-bit byte-range hashing and by other hash mixers that need wide-product diffusion. Depends on `<cstdint>` and MSVC intrinsics when relevant.

Risks: Fallback arithmetic must exactly emulate wide multiplication without overflow mistakes. Compiler/architecture detection affects both performance and hash output consistency.

Test signals: Cross-check `mulx` against `__uint128_t` on platforms that support it; compile MSVC x64/ARM64 and non-128-bit fallback paths; verify known values including zero, max, and mixed high-bit operands.
