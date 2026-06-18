# sources/user-network-fs/mergerfs/vendored/boost/config/requires_threads.hpp

Purpose: hard-fails compilation when a Boost component requiring threading is used without configured thread support.

Important APIs/macros: includes `boost/config.hpp` if needed, then emits compiler-specific `#error` messages when `BOOST_DISABLE_THREADS` is set or `BOOST_HAS_THREADS` is absent. Messages recommend flags for Comeau, Intel, GCC, SGI MIPSpro, DEC CXX, Borland, Metrowerks, SunPro, HP aCC, IBM VisualAge, and MSVC.

Control flow/dependencies: first handles explicit disable, including special GCC-on-HPUX/IRIX errors; otherwise checks missing `BOOST_HAS_THREADS` and selects a compiler-specific diagnostic branch.

State and persistence: compile-time error behavior only.

Integration points: Boost libraries that require threading include this header to fail early with an actionable message rather than compiling partially unsupported code.

Risks and test signals: risk is stale compiler flag advice and misspelled diagnostics. Test by compiling thread-requiring Boost headers with threads disabled or missing across major compilers, and with `BOOST_DISABLE_THREADS` explicitly set.
