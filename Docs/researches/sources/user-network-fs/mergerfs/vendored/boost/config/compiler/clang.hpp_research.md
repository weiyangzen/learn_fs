<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang.hpp

## Purpose
This compiler adapter maps Clang's feature-test intrinsics and target environment to Boost.Config macros.

## Important APIs, Types, And Control Flow
It normalizes `__has_extension`, `__has_attribute`, and `__has_cpp_attribute`, detects exceptions, RTTI, thread-local, stdint, float128/int128, branch prediction, symbol visibility, fallthrough, deprecation, aliasing, and unreachable support. It defines `BOOST_NO_CXX11_*`, `BOOST_NO_CXX14_*`, and `BOOST_NO_CXX17_*` when Clang feature probes or SD-6 macros are absent. It sets `BOOST_CLANG`, `BOOST_COMPILER`, and includes `clang_version.hpp` for normalized Apple/non-Apple versioning.

## State And Persistence
No runtime state exists; this is a macro-only configuration file.

## Dependencies And Integration Points
It is included by `boost/config.hpp` for Clang and also by Embarcadero's Clang-based path. It affects Boost.Assert through `BOOST_LIKELY`, symbol/export attributes, and source-location builtin choices.

## Risks And Test Signals
Risks include vendor Clang version skew, MSVC-compatible Clang target quirks, CUDA/NVCC int128 restrictions, and reliance on precise feature probes. Test signals are preprocessing under Apple Clang, upstream Clang, Clang-cl, CUDA-wrapped Clang, and language modes from C++03 through C++20.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang.hpp -->
