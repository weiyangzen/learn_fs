<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/mpw.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/mpw.hpp

## Purpose
This adapter configures Boost for classic MPW SCpp/MrCpp compilers.

## Important APIs, Types, And Control Flow
It sets `BOOST_COMPILER` based on `__SC__` or `__MRC__`, otherwise errors because the config was selected incorrectly. For MPW 8.90 or non-strict config it defines legacy defects covering cv specializations, dependent nested derivations, in-class member initialization, intrinsic wchar_t, partial specialization, using templates, cwchar, limits constants, and allocator quirks. It then defines broad C++11 absence macros and SD-6 checks for C++14/C++17 features.

## State And Persistence
All effects are preprocessor macros. There is no runtime state.

## Dependencies And Integration Points
It depends on MPW predefined macros and `MPW_CPLUS`. It is selected by Boost.Config for classic Mac MPW toolchains.

## Risks And Test Signals
Risks include old compiler assumptions, broad modern-feature disablement, and accidental selection for non-MPW compilers. Test signals are compile checks under SCpp/MrCpp, negative wrong-selection checks, and legacy template/stdlib feature tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/mpw.hpp -->
