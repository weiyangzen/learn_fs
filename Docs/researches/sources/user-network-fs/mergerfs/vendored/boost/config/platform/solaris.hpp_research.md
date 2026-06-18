# sources/user-network-fs/mergerfs/vendored/boost/config/platform/solaris.hpp

Purpose: configures Boost for Sun Solaris.

Important APIs/macros: defines `BOOST_PLATFORM "Sun Solaris"`, `BOOST_HAS_GETTIMEOFDAY`, `BOOST_HAS_UNISTD_H`, then includes POSIX detection. It removes `BOOST_HAS_PTHREADS` for GCC builds where `_POSIX_THREADS` is present but `_PTHREADS` is not, and explicitly enables `BOOST_HAS_STDINT_H`, `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, `BOOST_HAS_LOG1P`, and `BOOST_HAS_EXPM1`.

Control flow/dependencies: POSIX detection followed by Solaris/GCC thread correction and forced Solaris capabilities.

State and persistence: compile-time macros only.

Integration points: selected for `sun` or `__sun`; pairs with `compiler/sunpro_cc.hpp` or GCC/Clang configs.

Risks and test signals: risk is requiring correct compiler flags for pthreads, especially GCC `-pthreads`. Test thread detection with and without `_PTHREADS`, stdint, math functions, and mutex attributes.
