<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/compaq_cxx.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/compaq_cxx.hpp

## Purpose
This small adapter configures Boost for Compaq C++.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER` from `__DECCXX_VER`, marks `BOOST_NO_CXX11_VARIADIC_MACROS`, and rejects compilers older than version 6.5 with `#error`. There are no type or function declarations.

## State And Persistence
The header only sets preprocessor macros. It has no runtime state.

## Dependencies And Integration Points
It depends on the Compaq predefined `__DECCXX_VER` and is selected by Boost.Config compiler detection. Downstream Boost code uses the resulting compiler identity and defect macro.

## Risks And Test Signals
Risks are minimal but include lack of detailed feature detection and stale assumptions for versions above the supported baseline. Test signals are preprocessing under Compaq C++ and a negative compile test for old version macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/compaq_cxx.hpp -->
