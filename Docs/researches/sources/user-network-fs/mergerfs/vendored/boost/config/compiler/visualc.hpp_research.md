# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/visualc.hpp

Purpose: configures Boost for Microsoft Visual C++ and compatible compilers that define `_MSC_VER`.

Important APIs/macros: defines `BOOST_MSVC`, `BOOST_MSVC_FULL_VER`, `BOOST_COMPILER`, `BOOST_UNREACHABLE_RETURN`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_LONG_LONG`, `BOOST_HAS_NRVO`, `BOOST_HAS_PRAGMA_ONCE`, `BOOST_HAS_PRAGMA_DETECT_MISMATCH`, `BOOST_DEPRECATED(msg)`, ABI prefix/suffix headers, and `BOOST_CXX_VERSION`. It disables features by `_MSC_VER`, `_MSC_FULL_VER`, and `_MSVC_LANG`, including older C++11 constructs, value initialization, two-phase lookup, SFINAE expressions, C++14 constexpr, and early C++17 features. It also handles exception/RTTI mode macros and WinCE/CLR special cases.

Control flow/dependencies: selected last in compiler selection because many compilers emulate `_MSC_VER`. The file is ordered from core version normalization, to language/runtime features, to ABI, language-version reporting, and diagnostic messages for future versions.

State and persistence: compile-time macro state only.

Integration points: pairs with `platform/win32.hpp` and usually `stdlib/dinkumware.hpp`. ABI macros include `boost/config/abi/msvc_prefix.hpp` and suffix when not overridden.

Risks and test signals: risk centers on MSVC compatibility modes, clang-cl, and future `_MSC_VER` values. Tests should cover `/permissive-`, `/std:` modes, exceptions/RTTI toggles, CLR, WinCE, and Boost auto-link/ABI behavior.
