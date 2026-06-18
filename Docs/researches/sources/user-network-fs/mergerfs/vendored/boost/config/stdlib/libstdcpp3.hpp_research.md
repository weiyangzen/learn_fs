# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libstdcpp3.hpp

Purpose: configures Boost for GNU libstdc++ version 3 and newer.

Important APIs/macros: identifies libstdc++ through `__GLIBCPP__` or `__GLIBCXX__`, defines a `BOOST_STDLIB` string, handles extension namespace and C++ library header availability, and maps libstdc++ release macros, language mode, and feature-test macros to `BOOST_NO_CXX11/14/17/20/23_*`. It covers headers such as array, chrono, thread, tuple, type_traits, unordered containers, shared_mutex, optional, string_view, variant, any, filesystem, charconv, execution, memory_resource, and newer C++20/23 headers. It also handles deprecated C++98 facilities and special compiler/library combinations.

Control flow/dependencies: primarily preprocessor version and `__has_include` checks, sometimes relying on `<version>` having been included by the selector/suffix path.

State and persistence: compile-time standard-library state only.

Integration points: selected for GCC/libstdc++ and many Clang-on-Linux builds unless libc++ is used. Its macros are normalized by `suffix.hpp` and drive large parts of Boost's standard-library adaptation.

Risks and test signals: risk is distro-patched libstdc++ and mismatch between compiler language mode and library feature macros. Test GCC/Clang with libstdc++ in C++03 through C++23 modes, old dual ABI versions, filesystem/charconv/execution availability, shared_mutex, and deprecated auto_ptr/binders switches.
