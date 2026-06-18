<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/metrowerks.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/metrowerks.hpp

## Purpose
This adapter configures Boost for Metrowerks CodeWarrior C++.

## Important APIs, Types, And Control Flow
It disables locale when `_MSL_NO_LOCALE` is set, marks older-version template and SFINAE defects, detects intrinsic wchar and exception support through `__option`, maps `__MWERKS__` values to readable compiler versions, optionally enables rvalue references, defines broad C++11 absence macros, and uses SD-6 checks for C++14/C++17 features. It sets `BOOST_COMPILER`, rejects versions before 5.3, and optionally errors on unknown newer versions.

## State And Persistence
The header is macro-only. No runtime state exists.

## Dependencies And Integration Points
It depends on Metrowerks predefined macros and `__option`. Boost.Config uses it to select workaround paths for older CodeWarrior toolchains.

## Risks And Test Signals
Risks include old compiler support assumptions, strict-config differences, and feature detection tied to proprietary `__option` values. Test signals include compile checks across known CodeWarrior versions for templates, exceptions, wchar_t, rvalue references, and C++11 defect macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/metrowerks.hpp -->
