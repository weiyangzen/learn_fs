# sources/user-network-fs/mergerfs/vendored/boost/config/platform/irix.hpp

Purpose: configures Boost for SGI IRIX.

Important APIs/macros: defines `BOOST_PLATFORM "SGI Irix"`, disables `swprintf` with `BOOST_NO_SWPRINTF`, explicitly enables `BOOST_HAS_GETTIMEOFDAY` and `BOOST_HAS_PTHREAD_MUTEXATTR_SETTYPE`, and disables threads for GNU C++ on IRIX.

Control flow/dependencies: small fixed configuration plus `BOOST_HAS_UNISTD_H` and `detail/posix_features.hpp`.

State and persistence: compile-time platform state only.

Integration points: pairs with `compiler/sgi_mipspro.hpp` for native compiler builds. `suffix.hpp` may remove thread support if no supported thread API remains.

Risks and test signals: risk is legacy toolchain scarcity and differences between native MIPSpro and GCC on IRIX. Test `swprintf`, pthread mutex attributes, gettimeofday, and thread-disable behavior under both compilers.
