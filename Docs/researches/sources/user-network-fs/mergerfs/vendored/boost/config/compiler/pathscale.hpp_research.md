# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pathscale.hpp

Purpose: configures Boost for the PathScale EKOPath C++ compiler. It sets `BOOST_COMPILER` and then chooses one of two paths: PathCC 6 and newer delegate to `boost/config/compiler/clang.hpp`, while PathCC 4 and 5 define an explicit legacy feature profile.

Important APIs/macros: the file exports only preprocessor configuration macros. The legacy branch enables POSIX and math capability macros such as `BOOST_HAS_UNISTD_H`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_EXPM1`, and `BOOST_HAS_LOG1P`; it also marks many C++11 features and headers unavailable with `BOOST_NO_CXX11_*`. C++14 and C++17 support is tested with SD-6 feature-test macros such as `__cpp_constexpr`, `__cpp_structured_bindings`, and `__cpp_if_constexpr`.

Control flow/dependencies: selected by `detail/select_compiler_config.hpp` when `__PATHSCALE__` and `__PATHCC__ >= 4` are present. The `__PATHCC__ >= 6` branch reuses Clang configuration, so downstream behavior depends on `clang.hpp`; older branches are local macro assignments.

State and persistence: all behavior is compile-time macro state. There is no runtime state or persistence.

Integration points: `boost/config.hpp` consumes the feature macros, and `detail/suffix.hpp` later normalizes implication macros and thread availability.

Risks and test signals: risk is stale feature assumptions for a rare compiler. Useful tests are preprocessing with representative `__PATHCC__` values and compiling Boost.Config feature probes for PathCC 4/5 versus the Clang-based PathCC 6 path.
