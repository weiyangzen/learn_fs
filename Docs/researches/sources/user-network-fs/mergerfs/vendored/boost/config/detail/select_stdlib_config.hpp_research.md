# sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_stdlib_config.hpp

Purpose: selects the standard-library-specific Boost.Config header by defining `BOOST_STDLIB_CONFIG`.

Important APIs/macros: includes `<version>`, `<cstddef>`, or `<stddef.h>` to expose library macros, then detects STLPort, Comeau STL, Rogue Wave, libc++, GNU libstdc++ 3, generic SGI STL, Metrowerks MSL, IBM z/OS XL stdlib, IBM VisualAge stdlib, Modena, and Dinkumware/MSVC STL.

Control flow/dependencies: STLPort is checked first because it can sit on top of another library. If no library macro is visible after the first probe, it includes `<utility>` to expose C++-specific library macros. A disabled include list exists for dependency scanners.

State and persistence: compile-time selection only.

Integration points: `boost/config.hpp` includes the selected stdlib config unless disabled or overridden. The selected header contributes `BOOST_NO_CXX*_HDR_*`, namespace, allocator, locale, and extension container macros.

Risks and test signals: risk is accidental detection of an underlying vendor library instead of an adapter library. Test with libc++, libstdc++, MSVC STL, STLPort-over-Dinkumware, IBM, and Rogue Wave by verifying `BOOST_STDLIB_CONFIG` and `BOOST_STDLIB`.
