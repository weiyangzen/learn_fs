# sources/user-network-fs/mergerfs/vendored/boost/config/detail/select_compiler_config.hpp

Purpose: selects the compiler-specific Boost.Config header by defining `BOOST_COMPILER_CONFIG`.

Important APIs/macros: emits only `BOOST_COMPILER_CONFIG` and, for CUDA, directly includes `boost/config/compiler/nvcc.hpp`. It recognizes GCC-XML, Cray, Comeau, PathScale, Intel, Clang, Digital Mars, Diab, PGI, GCC, Kai, SGI MIPSpro, Compaq, Green Hills, CodeGear, Borland, Metrowerks, SunPro, HP aCC, MPW, IBM z/OS XL, IBM clang-based XL, IBM VisualAge/legacy XL, and MSVC.

Control flow/dependencies: an ordered `#if/#elif` chain. Ordering is critical: compiler emulation cases appear before the compilers they emulate, and `_MSC_VER` is last because many vendors define it. A disabled `#if 0` block lists all possible includes for dependency scanners.

State and persistence: compile-time selection only.

Integration points: `boost/config.hpp` includes the selected header unless user config bypasses compiler detection.

Risks and test signals: risk is detection-order regression for emulating compilers. Test by preprocessing under clang-cl, Intel, IBM XL, PGI, PathScale, and MSVC and verifying the selected `BOOST_COMPILER_CONFIG`.
