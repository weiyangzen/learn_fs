# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/sgi.hpp

Purpose: configures Boost for the generic SGI STL.

Important APIs/macros: validates `__STL_CONFIG_H`, defines `BOOST_STDLIB "SGI standard library"`, marks missing iterator traits, stringstream, locale, messages facet, templated iterator constructors, std allocator, std iterator, limits, and std::wstring based on SGI STL/compiler macros. It enables `BOOST_HAS_HASH`, `BOOST_HAS_SLIST`, and `BOOST_HAS_SGI_TYPE_TRAITS`, and disables most C++11 standard headers/facilities plus C++14 shared mutex/exchange and C++17 apply/invoke/iterator traits.

Control flow/dependencies: may include `no_tr1/utility.hpp`, `<unistd.h>`, and `<string>` depending on platform/compiler checks.

State and persistence: compile-time standard-library state only.

Integration points: selected when `__STL_CONFIG_H` is detected and not STLPort. Feeds extension container and SGI type-trait support into older Boost code.

Risks and test signals: risk is old libstdc++2/SGI STL edge cases and Apple macros. Test hash/slist headers, type traits, iterator traits, locale/messages, stringstream, and wide string support.
