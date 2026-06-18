# sources/user-network-fs/mergerfs/vendored/boost/config/platform/bsd.hpp

Purpose: configures Boost for FreeBSD, NetBSD, OpenBSD, and DragonFly BSD.

Important APIs/macros: validates BSD identity, defines `BOOST_PLATFORM` with the specific BSD and version macro, conditionally enables `BOOST_HAS_NL_TYPES_H` and `BOOST_HAS_PTHREADS`, handles NetBSD libstdc++ `swprintf` visibility, and sets POSIX capabilities such as `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_SIGACTION`, and `BOOST_HAS_CLOCK_GETTIME`. It may define `BOOST_NO_CWCHAR` and `BOOST_NO_CTYPE_FUNCTIONS`.

Control flow/dependencies: BSD-specific conditionals, then `BOOST_HAS_UNISTD_H` and `detail/posix_features.hpp`.

State and persistence: compile-time platform macros only.

Integration points: selected by platform selector for BSD macros. It feeds POSIX/thread availability into `suffix.hpp`.

Risks and test signals: risk is version checks lagging newer BSD releases or OpenBSD/DragonFly ctype differences. Test cwchar, ctype functions, pthreads, timers, and platform string generation per BSD.
