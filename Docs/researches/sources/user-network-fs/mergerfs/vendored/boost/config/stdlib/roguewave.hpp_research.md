# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/roguewave.hpp

Purpose: configures Boost for Rogue Wave standard libraries.

Important APIs/macros: defines `BOOST_RW_STDLIB`, normalizes `_RWSTD_VER` into `BOOST_RWSTD_VER`, defines `BOOST_STDLIB`, and applies version-specific workarounds for namespace support, allocator, iterator traits, locale/facet use, stringstream, wide-character support, long long numeric limits, and template instantiation behavior. It marks C++11 headers/facilities, C++14 shared mutex/exchange, and C++17 apply/invoke/iterator traits unavailable.

Control flow/dependencies: validates with `__STD_RWCOMPILER_H__` or `_RWSTD_VER`, possibly through `no_tr1/utility.hpp`; then uses version thresholds and compiler/library macros.

State and persistence: compile-time standard-library state only.

Integration points: selected by `select_stdlib_config.hpp` for Rogue Wave macros. Downstream Boost code uses its facet and locale macros through `suffix.hpp` helpers.

Risks and test signals: risk is old vendor variants with incompatible `_RWSTD_VER` encodings. Test version normalization, locale/use_facet macros, iterator traits, allocator, wstring/wstreambuf, and absence of C++11+ headers.
