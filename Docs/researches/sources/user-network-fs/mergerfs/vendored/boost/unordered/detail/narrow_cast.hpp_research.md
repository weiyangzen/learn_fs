# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/narrow_cast.hpp

## Purpose

This header defines `boost::unordered::detail::narrow_cast`, a constrained integral narrowing helper for Boost.Unordered internals. It documents and enforces the assumption that a conversion intentionally drops high bits from an integral source whose type is at least as wide as the destination.

## Important APIs, types, and functions

`template<typename To, typename From> constexpr To narrow_cast(From x) noexcept` is the only API. It uses `BOOST_UNORDERED_STATIC_ASSERT` to require `From` and `To` to be integral and `sizeof(From) >= sizeof(To)`. The returned value is a `static_cast<To>`.

Under `__MSVC_RUNTIME_CHECKS`, the expression masks `x` with an unsigned all-ones mask for the target type before casting. This suppresses Visual Studio's runtime check for data loss when the narrowing is deliberate.

## Control Flow

The function has no runtime control flow in normal builds. Compile-time assertions reject invalid type combinations. In MSVC runtime-check builds, the return expression includes a target-width mask generated through `std::make_unsigned<To>`.

## State and Persistence Behavior

The header is stateless and inline-only. It does not allocate, cache, mutate globals, or persist any values.

## Dependencies and Integration Points

It depends on `boost/unordered/detail/static_assert.hpp`, `boost/config.hpp`, and `<type_traits>`. It is used by low-level unordered implementation code that needs explicit narrowing without repeating assertions or carrying platform-specific MSVC runtime-check workarounds.

## Risks and Edge Cases

The helper does not check at runtime that the source value fits in `To`; it explicitly permits truncation. Signed inputs and signed destinations follow C++ conversion rules after the optional mask, so callers must not mistake this for a safe numeric cast. The size assertion prevents widening but does not distinguish value range differences between same-size signed and unsigned types.

## Test Signals

Compile-time tests should verify rejection of non-integral types and source types smaller than the destination. Runtime tests should cover truncation from 64 to 32 bits, signed and unsigned inputs, and Visual Studio runtime-check builds where the helper should not trigger narrowing diagnostics.
