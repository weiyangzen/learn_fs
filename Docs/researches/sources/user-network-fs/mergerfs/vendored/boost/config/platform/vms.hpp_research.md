# sources/user-network-fs/mergerfs/vendored/boost/config/platform/vms.hpp

Purpose: configures Boost platform macros for OpenVMS.

Important APIs/macros: include guard `BOOST_CONFIG_PLATFORM_VMS_HPP`, defines `BOOST_PLATFORM "OpenVMS"`, undefines `BOOST_HAS_STDINT_H`, enables `BOOST_HAS_UNISTD_H`, `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_DIRENT_H`, `BOOST_HAS_PTHREADS`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_LOG1P`, `BOOST_HAS_EXPM1`, and `BOOST_HAS_THREADS`, and undefines `BOOST_HAS_SCHED_YIELD`.

Control flow/dependencies: fixed macro table with no POSIX feature include.

State and persistence: compile-time platform state only.

Integration points: selected by `__VMS`. Thread support is explicitly enabled and recognized by `suffix.hpp` because `BOOST_HAS_PTHREADS` is present.

Risks and test signals: risk is stdint absence and scheduler-yield behavior differing across OpenVMS versions. Test directory, pthread, clock, math, stdint, and sched_yield probes.
