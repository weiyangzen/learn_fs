# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/vacpp.hpp

Purpose: configures Boost for the IBM VisualAge default standard library.

Important APIs/macros: disables `BOOST_NO_STD_ALLOCATOR` for `__IBMCPP__ <= 501`, defines `BOOST_HAS_MACRO_USE_FACET` and `BOOST_NO_STD_MESSAGES`, optionally includes `<unistd.h>` on Unix-like systems, marks C++11 headers/facilities unavailable, disables C++14 shared mutex/exchange, disables C++17 apply/invoke/iterator traits, and defines `BOOST_STDLIB "Visual Age default standard library"`.

Control flow/dependencies: simple IBM version check, Unix platform include guard, then fixed legacy standard-library feature profile.

State and persistence: compile-time standard-library macros only.

Integration points: selected for `__IBMCPP__` when z/OS is not active. Pairs with `compiler/vacpp.hpp` and often `platform/aix.hpp`.

Risks and test signals: risk is assuming old VisualAge library limitations for newer IBM XL configurations. Test allocator, locale facet macros, messages facet, C++11 header availability, and Unix include behavior.
