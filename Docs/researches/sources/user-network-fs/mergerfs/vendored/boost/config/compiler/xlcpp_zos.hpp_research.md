# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/xlcpp_zos.hpp

Purpose: configures Boost for IBM z/OS XL C/C++ V2R1.

Important APIs/macros: validates `__IBMCPP__`, `__COMPILER_VER__`, and minimum supported `0x42010000`, defines `BOOST_COMPILER` and `BOOST_XLCPP_ZOS`, includes `<features.h>`, and marks many unsupported C++11/14/17 language features. It enables `BOOST_HAS_LOG1P`, `BOOST_HAS_EXPM1`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_NRVO`, `BOOST_HAS_LONG_LONG`, `BOOST_HAS_MS_INT64`, `BOOST_HAS_VARIADIC_TMPL`, `BOOST_HAS_STATIC_ASSERT`, `BOOST_HAS_RVALUE_REFS`, and `BOOST_HAS_DECLTYPE` when z/OS feature macros permit. It defines `BOOST_FORCEINLINE`, `BOOST_NOINLINE`, `BOOST_MAY_ALIAS`, `BOOST_LIKELY`, and `BOOST_UNLIKELY` when IBM attributes/builtins are available.

Control flow/dependencies: selected before generic IBM compiler configuration when `__MVS__` and `__COMPILER_VER__` are present. The file is strict about known compiler versions and emits `BOOST_ASSERT_CONFIG` errors for newer versions.

State and persistence: compile-time-only macros.

Integration points: pairs with `platform/zos.hpp` and `stdlib/xlcpp_zos.hpp`. The branch-prediction macros and type/feature flags feed generic Boost code.

Risks and test signals: risk is stale V2R1 assumptions and strict version rejection. Test z/OS builds with feature macros for RTTI, exceptions, long long, defaulted/deleted functions, attributes, and threading.
