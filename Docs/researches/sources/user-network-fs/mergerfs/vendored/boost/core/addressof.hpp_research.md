# sources/user-network-fs/mergerfs/vendored/boost/core/addressof.hpp

Purpose: Portable implementation of `boost::addressof`, bypassing overloaded `operator&` and using compiler builtins when available.

Important APIs, types, and functions: Public `addressof(T&)`; deleted rvalue overload when supported; internal `addrof`, `addrof_ref`, constexpr-detection helpers, and null pointer specializations.

Control flow: Compile-time selection uses `__builtin_addressof` when supported, otherwise chooses constexpr plain `&o` only when no overloaded address operator exists, falling back to the classic char-reference reinterpretation trick.

State and persistence behavior: Stateless pointer utility.

Dependencies and integration points: Used widely by Boost.Core and allocator/pointer utilities. Depends on Boost config/workaround and `<cstddef>` in fallback mode.

Risks: Fallback paths are compiler-workaround-heavy and touch strict-aliasing-sensitive code. Array and null pointer edge cases have special handling for old compilers.

Test signals: Address objects with overloaded member and non-member `operator&`, arrays, const/volatile/nullptr types, constexpr cases, and deleted rvalue behavior.
