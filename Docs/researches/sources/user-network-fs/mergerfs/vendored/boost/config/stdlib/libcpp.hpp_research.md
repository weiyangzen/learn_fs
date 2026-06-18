# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcpp.hpp

Purpose: configures Boost for LLVM libc++.

Important APIs/macros: validates `_LIBCPP_VERSION`, defines `BOOST_STDLIB`, enables `BOOST_HAS_THREADS`, and maps libc++ feature macros/version thresholds to `BOOST_NO_CXX11_*`, `BOOST_NO_CXX14_*`, `BOOST_NO_CXX17_*`, and newer header capability macros. It handles no variadics/template aliases, C++03 mode, old incomplete atomic/chrono/type_traits/future support, `BOOST_NO_STD_MESSAGES`, C++14 exchange/shared_mutex, C++17 optional/string_view/variant/execution/invoke, removed C++98 facilities, span issues, thread_local problems with old libc++abi/Linux, and iterator traits.

Control flow/dependencies: may include `<ciso646>` for detection and `<version>` when present. Uses `_LIBCPP_VERSION`, `__cplusplus`, `__has_include`, and `__cpp_lib_*` macros.

State and persistence: compile-time standard-library configuration only.

Integration points: selected by `_LIBCPP_VERSION`. Pairs with Clang, Apple Clang, and other libc++ users; `suffix.hpp` consumes its feature macros.

Risks and test signals: risk is version thresholds not matching vendor-patched libc++ distributions. Test across Apple and upstream libc++, C++03/11/14/17/20 modes, `<version>` presence, thread_local linking, shared_mutex, execution, invoke, and removed auto_ptr/binders/random_shuffle toggles.
