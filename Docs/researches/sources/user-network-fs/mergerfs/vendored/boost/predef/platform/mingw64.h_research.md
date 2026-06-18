# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw64.h

Purpose: Detects MinGW-w64.

Important APIs, types, and functions: Defines `BOOST_PLAT_MINGW64`, `BOOST_PLAT_MINGW64_AVAILABLE`, `BOOST_PLAT_MINGW64_EMULATED`, and `BOOST_PLAT_MINGW64_NAME`.

Control flow: When `__MINGW64__` exists, it includes `<_mingw.h>` and uses `__MINGW64_VERSION_MAJOR/MINOR` to build a Boost version if available. It records emulation if another platform detector already claimed the platform; otherwise it sets `BOOST_PLAT_MINGW64`.

State and persistence behavior: Compile-time macro state only.

Dependencies and integration points: Included by `platform.h`, related to aggregate `mingw.h`, and used by `windows_uwp.h` as a UWP capability signal for MinGW-w64 version 3 or later.

Risks: It does not distinguish 32-bit versus 64-bit code generation by itself; MinGW-w64 can target both. Combine with architecture macros when data model matters.

Test signals: Primary and optional emulated Predef test declarations.
