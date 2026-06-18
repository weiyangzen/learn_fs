<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang_version.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang_version.hpp

## Purpose
This helper defines a normalized `BOOST_CLANG_VERSION` integer for upstream Clang and Apple Clang.

## Important APIs, Types, And Control Flow
For non-Apple Clang it computes `__clang_major__ * 10000 + __clang_minor__ * 100 + __clang_patchlevel__ % 100`. For Apple Clang it first computes `BOOST_CLANG_REPORTED_VERSION`, then maps Apple/Xcode-reported ranges to approximate upstream Clang version numbers, finally undefining the temporary reported-version macro.

## State And Persistence
It creates only preprocessor macros. There is no runtime state.

## Dependencies And Integration Points
It depends on Clang predefined version macros and optional `__apple_build_version__`. `clang.hpp` includes it so downstream headers can gate features on `BOOST_CLANG_VERSION`, such as source-location builtins.

## Risks And Test Signals
Risks include stale Apple/Xcode mapping and patchlevel truncation. Test signals are preprocessing on representative Apple Clang releases and upstream Clang, verifying the numeric macro matches expected Boost feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/clang_version.hpp -->
