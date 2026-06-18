# sources/user-network-fs/mergerfs/vendored/boost/config/platform/linux.hpp

Purpose: configures Boost platform macros for Linux and glibc-like systems.

Important APIs/macros: defines `BOOST_PLATFORM "linux"`, includes `<cstdlib>` or `<stdlib.h>` to expose glibc macros, enables `BOOST_HAS_STDINT_H` for suitable glibc/GCC combinations, handles old Comeau-on-Linux namespace and `swprintf` issues, enables `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_NANOSLEEP`, and optionally `BOOST_HAS_PTHREAD_YIELD`. It may define `BOOST_NO_SWPRINTF` when glibc or feature macros do not expose it.

Control flow/dependencies: libc/version checks, `BOOST_HAS_UNISTD_H`, `detail/posix_features.hpp`, GNU extension macro compatibility definitions for non-GCC compilers parsing glibc headers.

State and persistence: compile-time platform macro state only.

Integration points: selected for Linux, GNU, and glibc macros except Cray. Feeds standard POSIX/thread/math support to all Linux Boost builds.

Risks and test signals: risk is glibc feature macro dependence and non-GCC compiler parsing compatibility. Test under GCC, Clang, ICC/NVHPC, Android exclusions, old glibc, and strict C++ modes for `swprintf`, pthread yield, stdint, and GNU extension aliases.
