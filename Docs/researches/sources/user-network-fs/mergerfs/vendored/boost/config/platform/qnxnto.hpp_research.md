# sources/user-network-fs/mergerfs/vendored/boost/config/platform/qnxnto.hpp

Purpose: configures Boost for QNX Neutrino.

Important APIs/macros: defines `BOOST_PLATFORM "QNX"`, `BOOST_HAS_UNISTD_H`, then includes POSIX feature detection. It deliberately undefines `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1` because QNX advertises XOpen conformance without those facilities. It enables `BOOST_HAS_PTHREADS`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_CLOCK_GETTIME`, and `BOOST_HAS_NANOSLEEP`.

Control flow/dependencies: POSIX detection followed by corrective undefines and explicit QNX capabilities.

State and persistence: compile-time platform state only.

Integration points: selected by `__QNXNTO__`. Thread and time capability macros feed Boost.Thread, Chrono, and filesystem-adjacent code.

Risks and test signals: risk is XOpen macro overclaim or newer QNX versions adding removed facilities. Test nl_types, log1p/expm1, pthread mutex attrs, clock_gettime, and nanosleep.
