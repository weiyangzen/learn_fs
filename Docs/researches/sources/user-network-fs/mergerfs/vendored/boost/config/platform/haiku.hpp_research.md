# sources/user-network-fs/mergerfs/vendored/boost/config/platform/haiku.hpp

Purpose: configures Boost platform macros for Haiku.

Important APIs/macros: defines `BOOST_PLATFORM "Haiku"`, `BOOST_HAS_UNISTD_H`, `BOOST_HAS_STDINT_H`, and conditionally `BOOST_HAS_THREADS`. It marks several C++11 features/headers unavailable: `BOOST_NO_CXX11_HDR_TYPE_TRAITS`, `BOOST_NO_CXX11_ATOMIC_SMART_PTR`, `BOOST_NO_CXX11_STATIC_ASSERT`, and `BOOST_NO_CXX11_VARIADIC_MACROS`. It explicitly enables `BOOST_HAS_SCHED_YIELD` and `BOOST_HAS_GETTIMEOFDAY`.

Control flow/dependencies: fixed macros followed by `detail/posix_features.hpp`.

State and persistence: compile-time macros only.

Integration points: selected when `__HAIKU__` is defined. Standard-library and compiler configs may override or add more specific C++ feature information.

Risks and test signals: risk is stale C++11 header assumptions as Haiku toolchains evolve. Test type_traits, atomic smart pointer, variadic macro, static assert, threads, and POSIX time APIs.
