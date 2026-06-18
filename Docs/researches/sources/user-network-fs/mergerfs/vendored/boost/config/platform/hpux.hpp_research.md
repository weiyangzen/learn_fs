# sources/user-network-fs/mergerfs/vendored/boost/config/platform/hpux.hpp

Purpose: configures Boost for HP-UX.

Important APIs/macros: defines `BOOST_PLATFORM "HP-UX"`, conditionally enables `BOOST_HAS_STDINT_H`, marks `BOOST_NO_SWPRINTF` or `BOOST_NO_CWCTYPE` depending on compiler/source macros, and handles threading differently for GCC versus HP aCC. After POSIX detection it force-enables many capabilities such as `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_SIGACTION`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1`. It sets `BOOST_HAS_NRVO` outside PA-RISC.

Control flow/dependencies: compiler/version conditionals, `BOOST_HAS_UNISTD_H`, `detail/posix_features.hpp`, then post-detection force macros.

State and persistence: compile-time platform state only.

Integration points: pairs with HP aCC or GCC compiler configs and drives POSIX/thread choices in `suffix.hpp`.

Risks and test signals: risk is HP-UX source-feature macro sensitivity and old GCC thread limitations. Test GCC versions, HP aCC, swprintf/cwctype, pthreads, timers, inttypes/stdint, and NRVO assumptions.
