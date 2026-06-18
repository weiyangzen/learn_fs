<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc.hpp

## Purpose
This adapter maps GNU C++ versions and language modes to Boost.Config feature macros.

## Important APIs, Types, And Control Flow
It computes `BOOST_GCC_VERSION`, defines `BOOST_GCC` unless compiling under CUDA, detects C++11 mode, handles GCC 3.x and pre-4.x defects, enables pragma once, long long, NRVO, branch prediction, visibility/import-export attributes, RTTI/typeid detection, int128/float128, C++11 feature availability by version thresholds, C++14 and C++17 SD-6 gates, fallthrough, unused, may-alias, unreachable, and deprecation attributes. It rejects GCC before 3.3 and optionally errors for versions newer than the known 8.1 table under `BOOST_ASSERT_CONFIG`.

## State And Persistence
State is preprocessor-only. It includes `<cstddef>` or `<stddef.h>` to detect libstdc++ float128 support.

## Dependencies And Integration Points
It depends on GCC predefined macros, `__cplusplus`, CUDA markers, MinGW/Darwin/platform macros, and libstdc++ macros. Boost.Assert uses its `BOOST_LIKELY` and source-location code may test `BOOST_GCC`.

## Risks And Test Signals
Risks include stale known-version ceiling, CUDA host-compiler exceptions, MinGW `thread_local` bugs, and mismatch between compiler language support and standard-library support. Test signals are preprocessing/compile tests across GCC versions, C++03-17 modes, MinGW 32-bit, CUDA host builds, and visibility/int128/float128 probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc.hpp -->
