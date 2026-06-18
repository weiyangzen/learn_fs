# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/mulx.hpp

## Purpose

This Boost.Unordered detail header provides a small multiplication-based bit mixer. It exposes `mulx64`, `mulx32`, and `mulx(std::size_t)` in `boost::unordered::detail`, selecting a 64-bit or 32-bit mixing path according to detected `std::size_t` width. The mixer is intended for hash-table internals where a hash value needs a cheap avalanche step based on the high and low halves of a product.

## Important APIs, types, and functions

`mulx64(boost::uint64_t, boost::uint64_t)` computes a full 128-bit product and returns low-half XOR high-half. It has platform-specific implementations for MSVC x64 (`_umul128`), MSVC ARM64 (`__umulh` plus the normal product), compilers with `__uint128_t`, and a portable 32-bit-limb fallback.

`mulx32(boost::uint32_t, boost::uint32_t)` multiplies to 64 bits and XORs the two 32-bit halves. Under `__MSVC_RUNTIME_CHECKS` it masks the low half before narrowing to avoid Visual Studio runtime narrowing diagnostics.

`mulx(std::size_t)` is the public convenience mixer. On detected 64-bit-or-larger architectures it calls `mulx64(x, 0x9E3779B97F4A7C15ull)`, the golden-ratio multiplier. On 32-bit architectures it calls `mulx32(x, 0xE817FB2Du)`, a multiplier cited from the referenced arXiv hashing paper.

## Control Flow

Most control flow is preprocessor-driven. The file first chooses the best `mulx64` implementation at compile time, then detects whether `SIZE_MAX` or `UINTPTR_MAX` implies a 64-bit `size_t`. `mulx` uses that temporary `BOOST_UNORDERED_64B_ARCHITECTURE` macro and undefines it before leaving the header.

The portable `mulx64` path splits both inputs into high and low 32-bit limbs, combines partial products, propagates carry from the middle limbs, and returns reconstructed low-half XOR high-half. There is no runtime branching outside the small 32-bit mask path selected for MSVC runtime checks.

## State and Persistence Behavior

The header is stateless. It defines only inline functions and temporary macros. No data is persisted, cached, allocated, or synchronized.

## Dependencies and Integration Points

It depends on Boost integer typedefs from `boost/cstdint.hpp`, C limits, and `<cstddef>`. On MSVC it includes `<intrin.h>`. The integration point is Boost.Unordered internals that need size-dependent hash mixing without depending on a heavier hashing component.

## Risks and Edge Cases

The architecture decision treats widths greater than 64 bits as 64-bit. That is intentional in the macro comment but would discard entropy above 64 bits if used on unusual platforms. The fallback arithmetic is subtle carry code; regressions would create platform-specific hash distribution differences. The MSVC intrinsic branches exclude clang-cl, so clang-cl relies on the `__uint128_t` or fallback path. The mixer is not cryptographic and should not be used as a security boundary.

## Test Signals

Useful tests compare `mulx64` fallback output against a known 128-bit implementation, verify `mulx32` against hand-computed products, and compile on MSVC x64/ARM64 plus GCC/Clang. Hash-table tests should look for stable behavior across 32-bit and 64-bit builds, reasonable bucket distribution, and absence of runtime-check narrowing failures on Visual Studio.
