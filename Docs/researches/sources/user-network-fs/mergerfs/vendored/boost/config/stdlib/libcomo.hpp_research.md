# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/libcomo.hpp

Purpose: configures Boost for the Comeau standard library.

Important APIs/macros: validates `__LIBCOMO__`, defines `BOOST_STDLIB`, handles old `std::wstreambuf` and Windows `swprintf` issues, enables `BOOST_HAS_HASH` and `BOOST_HAS_SLIST` for newer versions, marks all C++11 headers and library facilities unavailable, disables C++14 shared mutex/exchange and C++17 apply/invoke/iterator traits, and defines `BOOST_HAS_SGI_TYPE_TRAITS`.

Control flow/dependencies: may include `boost/config/no_tr1/utility.hpp` to expose `__LIBCOMO__`; then uses `__LIBCOMO_VERSION__` thresholds and fixed missing-feature macros.

State and persistence: compile-time standard-library state only.

Integration points: selected by `select_stdlib_config.hpp` for `__LIBCOMO__`. Influences old extension container detection and type-traits paths.

Risks and test signals: risk is obsolete library support and broad disabling of C++11+ features. Test version detection, hash/slist availability, wstreambuf, swprintf on Windows, and absence of modern headers.
