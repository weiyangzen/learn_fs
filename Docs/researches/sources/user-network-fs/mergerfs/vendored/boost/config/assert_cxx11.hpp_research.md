<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx11.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx11.hpp

## Purpose
This generated header validates that Boost.Config does not report missing C++11 compiler or standard-library features.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx03.hpp`, so C++03 validation is a prerequisite. It then checks `BOOST_NO_CXX11_*` macros for language features such as `auto`, `constexpr`, `decltype`, defaulted/deleted functions, lambdas, `nullptr`, range-for, rvalue references, scoped enums, SFINAE expressions, variadic templates/macros, `alignas`, `alignof`, `noexcept`, thread-local, and unrestricted unions. It also checks C++11 library headers such as `<array>`, `<atomic>`, `<chrono>`, `<condition_variable>`, `<future>`, `<mutex>`, `<thread>`, `<tuple>`, type traits, and unordered containers.

## State And Persistence
No runtime state exists; the header is a compile-time conformance gate.

## Dependencies And Integration Points
It relies on Boost.Config compiler and stdlib configs. It is useful in CI or configure probes where mergerfs or vendored Boost code requires a true C++11-capable environment.

## Risks And Test Signals
Risks are false failures on partial standard-library implementations and stale vendored compiler support tables. Test signals are C++11 compilation under GCC/Clang/MSVC and negative tests by defining representative `BOOST_NO_CXX11_*` macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx11.hpp -->
