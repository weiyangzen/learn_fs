# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/dinkumware.hpp

Purpose: configures Boost for Dinkumware and the Microsoft STL family.

Important APIs/macros: validates detection through `_YVALS` or `_CPPLIB_VER`, defines `BOOST_DINKUMWARE_STDLIB`, `BOOST_MSSTL_VERSION`, and `BOOST_STDLIB`, sets namespace/allocator/locale workarounds, maps `BOOST_STD_EXTENSION_NAMESPACE` to `stdext` for newer MSVC, and marks standard headers/features unavailable by `_CPPLIB_VER`, `_HAS_CXX17`, `_HAS_CXX20`, `_MSVC_STL_UPDATE`, `_MSVC_STL_VERSION`, and related macros. It handles deprecated C++98 facilities (`BOOST_NO_AUTO_PTR`, binders, `random_shuffle`), CLR exclusions, codecvt deprecation, pointer traits, addressof, shared mutex, C++17 apply/invoke/iterator traits, and C++20 concepts.

Control flow/dependencies: may include `no_tr1/utility.hpp`, `<exception>`, and `<typeinfo>` in special no-exception MSVC/clang-cl cases. Most logic is version thresholds.

State and persistence: compile-time standard-library state only.

Integration points: selected for MSVC STL/Dinkumware. Pairs with `compiler/visualc.hpp` and `platform/win32.hpp`, but also supports other compilers using Dinkumware.

Risks and test signals: high risk due to many MSVC STL version and language-mode combinations. Test VS2010 through current, clang-cl, `_HAS_CXX17/_HAS_CXX20`, CLR, no exceptions, deprecated facility toggles, codecvt, shared_mutex, pointer_traits, and feature-test macros.
