# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sunpro_cc.hpp

Purpose: configures Boost for Sun/Oracle Studio C++ (`__SUNPRO_CC`). It encodes version-specific workarounds from early SunPro 5.x through Oracle Studio 12.6-era values.

Important APIs/macros: exports `BOOST_COMPILER`, `BOOST_SYMBOL_EXPORT`, `BOOST_SYMBOL_IMPORT`, `BOOST_SYMBOL_VISIBLE`, and `BOOST_DEPRECATED(msg)`. It defines many `BOOST_NO_*` and `BOOST_NO_CXX11/14/17_*` macros for missing or unreliable features, including in-class initialization, SFINAE expressions, two-phase lookup, variadic templates, ref qualifiers, thread-local storage, and C++17 structured bindings/inline variables/fold expressions. It also enables `BOOST_HAS_LONG_LONG` and conditionally `BOOST_HAS_THREADS` for Solaris 12 with Studio 12.4+.

Control flow/dependencies: selected by `detail/select_compiler_config.hpp` on `__SUNPRO_CC`. The flow is a sequence of version thresholds, then shared object/deprecation support, then modern feature-test macro checks, then version validation.

State and persistence: compile-time-only macro state.

Integration points: pairs with Solaris platform configuration and `suffix.hpp` normalization. Visibility/deprecation macros are consumed by exported Boost libraries.

Risks and test signals: risk is over-disabling features for newer Oracle Developer Studio or under-disabling broken partial implementations. Test via Boost.Config feature tests across `__SUNPRO_CC` versions, especially value initialization, SFINAE, deprecation attributes, visibility, and thread support.
