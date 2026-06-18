# sources/user-network-fs/mergerfs/vendored/boost/config/platform/cygwin.hpp

Purpose: configures Boost for Cygwin, treating it as POSIX-like rather than native Win32.

Important APIs/macros: defines `BOOST_PLATFORM "Cygwin"`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_LOG1P`, `BOOST_HAS_EXPM1`, and `BOOST_HAS_UNISTD_H`. It includes `<unistd.h>` to choose pthreads versus Win32 threads, may define `BOOST_HAS_PTHREADS`, `BOOST_HAS_SCHED_YIELD`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_WINTHREADS`, and `BOOST_HAS_FTIME`. It detects `<stdint.h>` through `<sys/types.h>`, handles older Cygwin `BOOST_NO_FENV_H`, and disables shared mutex when pthread visibility macros are insufficient.

Control flow/dependencies: includes `<unistd.h>`, `<sys/types.h>`, `<cygwin/version.h>`, possibly `<pthread.h>`, then `detail/posix_features.hpp`; finally undefines `BOOST_HAS_NL_TYPES_H`.

State and persistence: compile-time platform state only.

Integration points: selected before Win32. Feeds both POSIX and Windows-adjacent thread behavior into Boost.

Risks and test signals: risk is Cygwin version and feature macro dependence. Test pthread versus WinThread selection, `shared_mutex` availability, fenv, stdint, and `nl_types` absence.
