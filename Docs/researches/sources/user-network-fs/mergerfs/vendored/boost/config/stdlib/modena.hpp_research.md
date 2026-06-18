# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/modena.hpp

Purpose: configures Boost for the Modena C++ standard library.

Important APIs/macros: validates Modena detection through `MSIPL_COMPILE_H`, defines `BOOST_STDLIB`, and marks a broad set of standard-library facilities unavailable, especially C++11 headers, allocator/pointer traits/smart pointer/addressof/std::align, C++14 shared mutex/exchange, and C++17 apply/invoke/iterator traits.

Control flow/dependencies: may include `boost/config/no_tr1/utility.hpp` to expose the library macro, then applies a fixed legacy-library profile.

State and persistence: compile-time standard-library state only.

Integration points: selected by `select_stdlib_config.hpp` when `MSIPL_COMPILE_H` is found. Downstream Boost libraries use the `BOOST_NO_*` macros to avoid unavailable standard APIs.

Risks and test signals: risk is rare-library bit rot and unsupported modern standard facilities. Test detection, locale/iterator/allocator basics, and compile probes for all headers marked unavailable if supporting Modena remains a requirement.
