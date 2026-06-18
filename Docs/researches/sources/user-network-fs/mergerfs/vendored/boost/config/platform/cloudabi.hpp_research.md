# sources/user-network-fs/mergerfs/vendored/boost/config/platform/cloudabi.hpp

Purpose: declares Boost platform capabilities for Nuxi CloudABI.

Important APIs/macros: defines `BOOST_PLATFORM "CloudABI"` and enables headers/functions including `BOOST_HAS_DIRENT_H`, `BOOST_HAS_STDINT_H`, `BOOST_HAS_UNISTD_H`, `BOOST_HAS_CLOCK_GETTIME`, `BOOST_HAS_EXPM1`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_LOG1P`, `BOOST_HAS_NANOSLEEP`, `BOOST_HAS_PTHREADS`, and `BOOST_HAS_SCHED_YIELD`.

Control flow/dependencies: fixed macro table with no includes.

State and persistence: compile-time platform state only.

Integration points: selected when `__CloudABI__` is defined. `suffix.hpp` validates threading and derives standard helpers.

Risks and test signals: CloudABI is discontinued/niche, so the risk is stale feature declarations. Test by compiling probes for directory, pthread, clock, and math APIs with the CloudABI SDK if supported.
