# sources/user-network-fs/mergerfs/vendored/boost/config/platform/zos.hpp

Purpose: configures Boost platform macros for IBM z/OS.

Important APIs/macros: defines `BOOST_PLATFORM "IBM z/OS"`, includes `<features.h>`, conditionally enables `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_THREADS`, and `BOOST_HAS_SCHED_YIELD`, and always enables `BOOST_HAS_SIGACTION`, `BOOST_HAS_UNISTD_H`, `BOOST_HAS_DIRENT_H`, and `BOOST_HAS_NL_TYPES_H`.

Control flow/dependencies: z/OS feature macros such as `__UU`, `_OPEN_THREADS`, `__SUSV3_THR`, and `__SUSV3` drive capability macros.

State and persistence: compile-time macro state only.

Integration points: pairs with `compiler/xlcpp_zos.hpp` and `stdlib/xlcpp_zos.hpp`. Thread and POSIX macros feed `suffix.hpp` validation.

Risks and test signals: risk is z/OS feature-mode dependence. Test with and without Unix System Services/thread feature macros, plus sigaction, dirent, nl_types, sched_yield, and gettimeofday probes.
