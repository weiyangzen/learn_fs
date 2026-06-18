<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/intel.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/intel.hpp

## Purpose
This adapter configures Boost for Intel C++, accounting for whether Intel is emulating MSVC, GCC, or using an older EDG path.

## Important APIs, Types, And Control Flow
For Intel 15+ with MSVC/GCC emulation, it includes the corresponding `visualc.hpp` or `gcc.hpp`, then undefines host compiler identity and applies Intel corrections. The fallback includes `common_edg.hpp` and performs detailed Intel version setup. It computes `BOOST_INTEL_CXX_VERSION`, C++0x mode, `BOOST_INTEL_GCC_VERSION`, `BOOST_COMPILER`, `BOOST_INTEL`, platform identity, legacy defects, wchar_t validation templates, RTTI/typeid detection, visibility, aliasing, C++11 feature undefines by Intel+host version combinations, known broken features, fenv support, stdint, int128, and known-version checks.

## State And Persistence
Almost all state is macro-only. In C++ mode it declares compile-time templates/typedefs to validate whether `wchar_t` is intrinsic, but they are type-only checks with no runtime storage.

## Dependencies And Integration Points
It depends on Intel, MSVC, GCC, EDG, platform, and CUDA macros and may include host compiler config headers. It is central for Boost portability under Intel compilers.

## Risks And Test Signals
Risks include complex host-emulation interactions, stale version ceiling, Intel version 9999 workaround, feature availability that depends on both Intel and host compiler versions, and CUDA C++03 int128 restrictions. Test signals are matrix compile tests under Intel/MSVC and Intel/GCC modes, C++03/11/14/17 modes, wchar_t validation, RTTI-off builds, and feature-specific tests for constexpr, rvalue refs, tuple/future, and int128.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/intel.hpp -->
