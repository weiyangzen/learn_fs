<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/digitalmars.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/digitalmars.hpp

## Purpose
This adapter configures Boost for Digital Mars C++.

## Important APIs, Types, And Control Flow
It sets `BOOST_COMPILER`, enables long long and pragma once, marks several legacy defects outside strict config, enables dirent/stdint/WinThreads and selected math functions, detects std namespace issues by including `<cstddef>`, detects exceptions, and defines broad C++11/C++14/C++17 absence macros. It rejects `__DMC__ <= 0x840` and optionally errors on unknown versions with `BOOST_ASSERT_CONFIG`.

## State And Persistence
The header emits only macros and may include `<cstddef>` for namespace detection. No runtime objects exist.

## Dependencies And Integration Points
It depends on `__DMC__`, `__DMC_VERSION_STRING__`, `_CPPUNWIND`, and STL vendor macros. It feeds Boost feature selection for Digital Mars builds.

## Risks And Test Signals
Risks include broad disabling of modern C++ features, std namespace detection via included headers, and old compiler support. Test signals are Boost.Config compile checks for exception mode, std namespace, WinThreads, math functions, and C++ feature gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/digitalmars.hpp -->
