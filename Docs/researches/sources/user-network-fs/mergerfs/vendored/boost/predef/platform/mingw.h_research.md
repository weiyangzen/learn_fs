# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw.h

Purpose: Detects any MinGW family platform and, where possible, its version.

Important APIs, types, and functions: Defines `BOOST_PLAT_MINGW`, `BOOST_PLAT_MINGW_AVAILABLE`, `BOOST_PLAT_MINGW_EMULATED`, and `BOOST_PLAT_MINGW_NAME`.

Control flow: If `__MINGW32__` or `__MINGW64__` is defined, it includes `<_mingw.h>`, prefers `__MINGW64_VERSION_MAJOR/MINOR`, then attempts 32-bit version macros, and falls back to generic availability. If another platform was already detected, it records `BOOST_PLAT_MINGW_EMULATED`; otherwise it assigns `BOOST_PLAT_MINGW` and includes `platform_detected.h`.

State and persistence behavior: Compile-time-only. It may leave both a primary platform marker and an emulation marker depending on include order.

Dependencies and integration points: Used by Windows and platform aggregation paths; MinGW compilers also interact with `BOOST_OS_WINDOWS`.

Risks: The 32-bit fallback condition checks `__MINGW32_VERSION_MAJOR/MINOR` but the value expression uses `__MINGW32_MAJOR_VERSION/MINOR_VERSION`, so version precision depends on those aliases existing in `_mingw.h`.

Test signals: Declares tests for the primary macro and, when present, the emulated macro.
