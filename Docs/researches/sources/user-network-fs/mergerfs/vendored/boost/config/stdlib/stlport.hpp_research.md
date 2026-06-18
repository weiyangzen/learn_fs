# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/stlport.hpp

Purpose: configures Boost for STLPort.

Important APIs/macros: validates `__SGI_STL_PORT` or `_STLPORT_VERSION`, defines `BOOST_STDLIB`, handles static constant initialization, partial specialization/iterator traits, stringstream/new iostreams, locale, TR1 unordered containers, member templates, allocator/rebind, wide-character/string support, SGI hash/slist extensions, standard C namespace imports, use_facet variants, Borland-specific fixes, and GCC 2 min/max ADL workarounds. It marks most C++11 headers/facilities, C++14 shared mutex/exchange, and C++17 apply/invoke/iterator traits unavailable.

Control flow/dependencies: may include `<cstddef>`, `<unistd.h>`, `<stdlib.h>`, `<string.h>`, and `<algorithm>` in targeted branches.

State and persistence: compile-time macros plus a few namespace using declarations for old Borland/GCC cases.

Integration points: selected before underlying libraries because STLPort may wrap another vendor STL. `suffix.hpp` uses its locale, allocator, wide-character, and extension container macros.

Risks and test signals: risk is wrapper-library detection, namespace import side effects, and compiler-specific old STLPort configurations. Test STLPort 4/5, Borland, GCC 2.95, namespace modes, hash/slist, locale facets, allocator, and wide-character support.
