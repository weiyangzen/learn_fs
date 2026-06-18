# sources/user-network-fs/mergerfs/vendored/boost/core/detail/static_assert.hpp

Purpose: Internal static assertion macro wrapper for Boost.Core.

Important APIs, types, and functions: Defines `BOOST_CORE_STATIC_ASSERT(expr)` as `static_assert(expr, #expr)` where available or `BOOST_STATIC_ASSERT(expr)` on older compilers.

Control flow: Compile-time preprocessor selection only.

State and persistence behavior: No state.

Dependencies and integration points: Includes Boost config and, for old compilers, Boost.StaticAssert. Used by `bit.hpp` and other core headers.

Risks: Error message differences across compiler modes; macro must be usable in class/function scopes.

Test signals: Compile passing and failing assertions in C++03 and C++11+ modes.
