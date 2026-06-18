<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx17.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx17.hpp

## Purpose
This generated header validates C++17 support as represented by Boost.Config defect macros.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp` and `boost/config/assert_cxx14.hpp`, then checks `BOOST_NO_CXX17_*` macros. The checks cover auto non-type template parameters, class template deduction guides, fold expressions, `if constexpr`, inline variables, structured bindings, iterator traits, `std::apply`, `std::invoke`, and C++17 library headers including `<any>`, `<charconv>`, `<execution>`, `<filesystem>`, `<memory_resource>`, `<optional>`, `<string_view>`, and `<variant>`.

## State And Persistence
It has no runtime state or persistence. Its behavior is compile-time validation only.

## Dependencies And Integration Points
It depends on the lower standard assertion chain and current Boost.Config compiler/stdlib selections. It integrates with CI/configure checks for code paths that require full C++17 support.

## Risks And Test Signals
Risks are library-specific false failures, especially `<charconv>`, `<execution>`, and `<filesystem>` on older libstdc++/libc++ releases. Test signals are compile-only checks under explicit C++17 mode and targeted negative macro injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx17.hpp -->
