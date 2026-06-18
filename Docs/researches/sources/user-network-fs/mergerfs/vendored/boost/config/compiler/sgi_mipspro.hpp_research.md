# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/sgi_mipspro.hpp

Purpose: configures Boost for the SGI IRIX MIPSpro C++ compiler.

Important APIs/macros: defines `BOOST_COMPILER` from `_COMPILER_VERSION`, includes `boost/config/compiler/common_edg.hpp`, enables `BOOST_HAS_THREADS`, and disables two-phase name lookup with `BOOST_NO_TWO_PHASE_NAME_LOOKUP`. It explicitly undefines `BOOST_NO_SWPRINTF` and `BOOST_DEDUCED_TYPENAME`, overriding defaults inherited from EDG/common configuration.

Control flow/dependencies: selected when `__sgi` is detected by `detail/select_compiler_config.hpp`. The meaningful compiler feature baseline comes from `common_edg.hpp`; this file applies SGI-specific threading and language corrections.

State and persistence: compile-time macro configuration only.

Integration points: platform selection will usually pair this with `platform/irix.hpp`, which contributes POSIX feature macros and may disable threads for GNU-on-IRIX builds. `detail/suffix.hpp` later validates whether an actual threading API was detected.

Risks and test signals: MIPSpro is legacy and hard to validate. Risks include mismatches between EDG defaults and the SGI front end. Test signals are Boost.Config compile probes for `swprintf`, dependent typename handling, thread macros, and two-phase lookup assumptions.
