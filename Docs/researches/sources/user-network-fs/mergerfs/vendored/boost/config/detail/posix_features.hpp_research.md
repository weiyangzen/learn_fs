# sources/user-network-fs/mergerfs/vendored/boost/config/detail/posix_features.hpp

Purpose: derives POSIX and X/Open capability macros from `<unistd.h>` feature macros.

Important APIs/macros: when `BOOST_HAS_UNISTD_H` is already set, includes `<unistd.h>` and may define `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_SIGACTION`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1`.

Control flow/dependencies: platform headers opt in by defining `BOOST_HAS_UNISTD_H` and including this file. Tests use `_XOPEN_VERSION`, `_POSIX_VERSION`, `_POSIX_THREADS`, `_POSIX_TIMERS`, `_XOPEN_REALTIME`, `_POSIX_PRIORITY_SCHEDULING`, `_POSIX_THREAD_PRIORITY_SCHEDULING`, and `_XOPEN_SOURCE`.

State and persistence: compile-time macro derivation only.

Integration points: reused by Unix-like platform configs such as AIX, BSD, Linux, macOS, Solaris, VxWorks, QNX, and generic Unix fallback.

Risks and test signals: risk is false positives from platforms that define POSIX macros but ship stubs or require feature macros before system headers. Test with preprocess-only and compile/link checks for pthreads, timers, directory headers, and math functions under each platform mode.
