# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp.hpp

Purpose: configures Boost for IBM XL C/C++ for Linux little-endian, which is clang based and identified separately from legacy `__IBMCPP__`.

Important APIs/macros: defines `BOOST_HAS_PRAGMA_ONCE`, optional `BOOST_HAS_PRAGMA_DETECT_MISMATCH`, `BOOST_NO_EXCEPTIONS`, `BOOST_NO_RTTI`, `BOOST_NO_TYPEID`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_NRVO`, `BOOST_HAS_LONG_LONG`, `BOOST_SYMBOL_EXPORT/IMPORT/VISIBLE`, `BOOST_LIKELY`, `BOOST_UNLIKELY`, and optionally `BOOST_FALLTHROUGH`. Feature gates are based on Clang `__has_feature`, `__has_extension`, `__has_cpp_attribute`, `__has_builtin`, and SD-6 macros.

Control flow/dependencies: selected when `__ibmxl__` is set and not treated as generic Clang. The file locally defines compatibility fallbacks for `__has_extension` and `__has_cpp_attribute`, then tests C++11/14/17 features one by one.

State and persistence: compile-time macros only.

Integration points: integrates with Boost visibility, branch-prediction, exception/RTTI, and feature-selection helpers. `suffix.hpp` consumes the feature macros to define portable wrappers such as `BOOST_NOEXCEPT` and `BOOST_CONSTEXPR`.

Risks and test signals: risk is that IBM's clang fork reports features differently from upstream Clang. Test with `__has_feature` probes for exceptions, RTTI, constexpr, generic lambdas, relaxed constexpr, and visibility attributes.
