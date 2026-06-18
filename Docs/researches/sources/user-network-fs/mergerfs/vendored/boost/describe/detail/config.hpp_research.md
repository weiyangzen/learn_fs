# sources/user-network-fs/mergerfs/vendored/boost/describe/detail/config.hpp

Purpose: Central feature/configuration macros for Boost.Describe.

Important APIs, types, and functions: Defines `BOOST_DESCRIBE_CXX11`, `BOOST_DESCRIBE_CXX14`, `BOOST_DESCRIBE_CONSTEXPR_OR_CONST`, `BOOST_DESCRIBE_MAYBE_UNUSED`, `BOOST_DESCRIBE_INLINE_VARIABLE`, and `BOOST_DESCRIBE_INLINE_CONSTEXPR`.

Control flow: Preprocessor detects language level, MSVC support, GCC 4.7 exclusion, Clang unused attributes, and inline variables.

State and persistence behavior: Compile-time macros only.

Dependencies and integration points: Included by all Boost.Describe headers to gate reflection metadata support.

Risks: Incorrect C++ level detection changes whether describe APIs exist at all. Inline variable support affects ODR behavior for descriptor constants.

Test signals: Compile C++03, C++11, C++14, and C++17 modes; verify macro values and descriptor definitions on MSVC/GCC/Clang.
