<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc_xml.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc_xml.hpp

## Purpose
This adapter configures Boost for GCC-XML, an older source-analysis compiler front end.

## Important APIs, Types, And Control Flow
It disables abstract detection for older GCC-XML GNU emulation, conditionally enables threads for unknown non-Linux/non-MinGW/non-MSVC platforms, marks long long support, and defines broad C++11 absence macros plus SD-6-based C++14/C++17 absence checks. It sets no runtime functions.

## State And Persistence
All effects are preprocessor macros. There is no runtime state or persistence.

## Dependencies And Integration Points
It depends on `__GCCXML_GNUC__`, `__GCCXML_GNUC_MINOR__`, platform macros, and C++ feature-test macros. It is selected by Boost.Config for analysis-tool builds, not normal mergerfs runtime builds.

## Risks And Test Signals
Risks are conservative modern C++ disabling and unconditional thread assumptions on unknown platforms. Test signals are GCC-XML preprocessing of Boost headers and negative checks for unsupported C++11 constructs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/gcc_xml.hpp -->
