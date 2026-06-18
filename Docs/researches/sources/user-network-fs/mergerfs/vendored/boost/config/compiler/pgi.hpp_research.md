# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/pgi.hpp

Purpose: adapts Boost.Config to the PGI/NVIDIA HPC C++ compiler. It treats PGI as mostly GCC-compatible, includes the GCC compiler configuration, and then corrects known PGI deviations.

Important APIs/macros: defines `BOOST_COMPILER_VERSION` from `__PGIC__` and `__PGIC_MINOR__`, and defines `BOOST_COMPILER` from that value. It then undefines `BOOST_HAS_FLOAT128` because PGI exposes `__float128` as a typedef rather than as a distinct type, and undefines `BOOST_HAS_INT128` because `__int128` is not supported.

Control flow/dependencies: selected by `detail/select_compiler_config.hpp` when `__PGI` is defined. The primary dependency is `boost/config/compiler/gcc.hpp`; this file is a correction layer on top of GCC-compatible defaults.

State and persistence: compile-time macro state only.

Integration points: the corrected `BOOST_HAS_*128` macros protect Boost code that overloads or specializes on extended arithmetic types. The compiler identity feeds diagnostics and optional `BOOST_ASSERT_CONFIG` reporting.

Risks and test signals: the main risk is inheriting too much from GCC if PGI diverges in newer releases. Test by compiling Boost.Config arithmetic-type probes and overload-resolution checks under PGI/NVIDIA HPC releases.
