# sources/user-network-fs/mergerfs/vendored/boost/config/platform/aix.hpp

Purpose: configures Boost platform macros for IBM AIX.

Important APIs/macros: defines `BOOST_PLATFORM "IBM Aix"`, POSIX/header capability macros including `BOOST_HAS_UNISTD_H`, `BOOST_HAS_NL_TYPES_H`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_CLOCK_GETTIME`, and `BOOST_HAS_STDINT_H`, plus pthread-related macros `BOOST_HAS_PTHREADS`, `BOOST_HAS_PTHREAD_DELAY_NP`, and `BOOST_HAS_SCHED_YIELD`.

Control flow/dependencies: static macro definitions followed by inclusion of `boost/config/detail/posix_features.hpp` to derive any additional POSIX capabilities from `<unistd.h>`.

State and persistence: compile-time-only platform state.

Integration points: selected by `detail/select_platform_config.hpp` for `_AIX` or IBM compiler contexts not already matched by z/OS. Works with IBM compiler and standard-library configs.

Risks and test signals: risk is assuming pthread and timer APIs across AIX version/libc modes. Test compile/link checks for pthread delay/yield, `clock_gettime`, `nanosleep`, and `<stdint.h>` integration.
