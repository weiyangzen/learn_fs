# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/msl.hpp

Purpose: configures Boost for Metrowerks MSL.

Important APIs/macros: validates `__MSL_CPP__`, defines `BOOST_STDLIB`, applies version-specific workarounds for C standard namespace, `swprintf`, `std::locale`, `std::messages`, `std::wstring`, and allocator behavior, and marks modern C++ standard headers and facilities unavailable where MSL lacks them.

Control flow/dependencies: detection may use a `no_tr1` wrapper to include a standard header, then conditionals use MSL version/configuration macros.

State and persistence: compile-time standard-library state only.

Integration points: commonly pairs with Metrowerks compiler and Mac platform configurations. `suffix.hpp` derives locale, wide-character, and allocator implication macros from this profile.

Risks and test signals: risk is old CodeWarrior/MSL version fragmentation. Test namespace imports, locale facets, wide strings, allocator/rebind support, `swprintf`, and modern header absence under supported MSL versions.
