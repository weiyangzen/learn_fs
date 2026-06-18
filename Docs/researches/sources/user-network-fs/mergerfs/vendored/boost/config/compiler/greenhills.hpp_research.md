<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/greenhills.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/greenhills.hpp

## Purpose
This adapter configures Boost for the Green Hills C++ compiler.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER` from `__ghs`, enables long long, and marks `BOOST_NO_CXX11_VARIADIC_MACROS`. There are no functions or type declarations.

## State And Persistence
The file is macro-only and has no runtime state.

## Dependencies And Integration Points
It depends on the Green Hills predefined `__ghs` macro and is selected through Boost.Config compiler detection.

## Risks And Test Signals
Risks include very limited feature coverage and potential under-reporting of compiler defects. Test signals are Boost.Config compile checks on Green Hills targets, especially variadic macro and long-long behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/greenhills.hpp -->
