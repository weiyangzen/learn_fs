# sources/user-network-fs/mergerfs/vendored/boost/config/platform/macos.hpp

Purpose: configures Boost for classic Mac OS, macOS, and Metrowerks/MSL combinations.

Important APIs/macros: defines `BOOST_PLATFORM "Mac OS"`. For Mach builds outside MSL, it enables `BOOST_HAS_UNISTD_H`, includes POSIX features, forces `BOOST_HAS_STDINT_H`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_SIGACTION`, and on GCC 4+ `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE` and `BOOST_HAS_NANOSLEEP`. It may define `BOOST_NO_STDC_NAMESPACE` for old GCC Apple modes. For Carbon/MSL it handles `BOOST_HAS_PTHREADS`, `BOOST_HAS_THREADS`, `BOOST_HAS_GETTIMEOFDAY`, and `BOOST_BIND_ENABLE_PASCAL`.

Control flow/dependencies: branches on `__MACH__` and `_MSL_USING_MSL_C`, then compiler/runtime-specific sections.

State and persistence: compile-time macros only.

Integration points: selected for `macintosh`, `__APPLE__`, or `__APPLE_CC__`. Works with compiler and MSL/libc++/libstdc++ stdlib configs.

Risks and test signals: risk is obsolete Carbon/MSL behavior versus modern Apple clang/libc++. Test POSIX APIs, pthread mutex attributes, namespace behavior, and platform selection on modern macOS and any supported legacy targets.
