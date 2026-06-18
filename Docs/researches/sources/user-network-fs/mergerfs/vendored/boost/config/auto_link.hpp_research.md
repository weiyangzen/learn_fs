<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/auto_link.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/auto_link.hpp

## Purpose
This header implements Boost's automatic library selection for MSVC, Borland/Embarcadero, Intel-on-MSVC, Metrowerks Windows, and Clang-cl on Windows. It emits compiler `#pragma comment(lib, ...)` directives so the linker picks the correct Boost binary.

## Important APIs, Types, And Control Flow
The caller must define `BOOST_LIB_NAME`; optional macros include `BOOST_LIB_TOOLSET`, `BOOST_DYN_LINK`, `BOOST_LIB_DIAGNOSTIC`, `BOOST_AUTO_LINK_NOMANGLE`, `BOOST_AUTO_LINK_TAGGED`, `BOOST_AUTO_LINK_SYSTEM`, and `BOOST_LIB_BUILDID`. The header selects a toolset tag, threading tag, runtime tag, architecture/address-model tag, library prefix, and suffix. It then emits a library name in one of the supported layouts: unmangled, tagged, system, build-id, or default full mangling. It errors on incompatible runtime/linkage combinations and missing required macros.

## State And Persistence
There is no runtime state. The persistent effect is a compiler/linker directive embedded in the object file. The header undefines most temporary macros afterward, while intentionally preserving user-supplied `BOOST_LIB_TOOLSET`.

## Dependencies And Integration Points
It includes `boost/config.hpp` and `boost/version.hpp` for compiler identity and Boost version. It integrates with separately compiled Boost libraries; mergerfs on Unix-like platforms likely bypasses it because it only acts for known Windows-style compilers.

## Risks And Test Signals
Risks include silently choosing a nonexistent binary name, `BOOST_DYN_LINK` with static runtime, STLport/debug Python tag mismatches, and no include guard by design. Test signals include preprocessing diagnostics with `BOOST_LIB_DIAGNOSTIC`, MSVC/Clang-cl object inspection for default library directives, and matrix builds for debug/release, static/dynamic, x86/x64.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/auto_link.hpp -->
