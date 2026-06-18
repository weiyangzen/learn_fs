# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/static_assert.hpp

## Purpose

This very small header centralizes Boost.Unordered's static assertion macro. It wraps C++ `static_assert` so internal headers can use a consistent project macro name and message style.

## Important APIs, types, and functions

`BOOST_UNORDERED_STATIC_ASSERT(...)` expands to `static_assert(__VA_ARGS__, #__VA_ARGS__)`. The expression text becomes the assertion message. The header also includes `boost/config.hpp` and enables `#pragma once` when `BOOST_HAS_PRAGMA_ONCE` is defined.

## Control Flow

There is no runtime control flow. The macro affects compilation only; failing assertions reject the translation unit.

## State and Persistence Behavior

The header has no state. It defines one macro guarded by include guards.

## Dependencies and Integration Points

It is included by other Boost.Unordered detail headers such as `narrow_cast.hpp`. The integration point is compile-time contract enforcement for internal templates.

## Risks and Edge Cases

The macro always stringizes the full variadic expression as the message, so custom explanatory messages are not supported through this wrapper. It also requires language support for C++11 `static_assert`, which is consistent with the surrounding vendored Boost.Unordered code.

## Test Signals

Compile-fail tests should verify that invalid template instantiations using this macro fail with the stringized condition. Include-order tests should verify the macro is available and does not conflict with other Boost headers.
