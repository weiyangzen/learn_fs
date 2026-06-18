# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/config.hpp

Purpose: Compiler/language feature detection and workaround definitions for Boost.MP11.

Important APIs, types, and functions: `BOOST_MP11_WORKAROUND`, compiler version macros for CUDA/Clang/Intel/GCC/MSVC, `BOOST_MP11_CONSTEXPR`, and feature flags such as constexpr availability, fold expressions, template auto, type-pack element, and C++14 constexpr.

Control flow: Preprocessor maps compiler predefined macros into normalized MP11 feature macros and disables/enables workarounds.

State and persistence behavior: Compile-time macros only.

Dependencies and integration points: Included by all MP11 detail and algorithm headers.

Risks: Incorrect feature detection changes template implementations and can break old compiler support. Some workarounds deliberately include unusual declarations such as `gets` for old Clang/libstdc++ combinations.

Test signals: Compile MP11 suite under supported compiler matrix; assert feature macros in representative modes.
