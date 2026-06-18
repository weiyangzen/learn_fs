# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/mingw32.h

Purpose: Detects the classic 32-bit MinGW platform.

Important APIs, types, and functions: Defines `BOOST_PLAT_MINGW32`, `BOOST_PLAT_MINGW32_AVAILABLE`, `BOOST_PLAT_MINGW32_EMULATED`, and `BOOST_PLAT_MINGW32_NAME`.

Control flow: When `__MINGW32__` exists, it includes `<_mingw.h>`, builds a version from `__MINGW32_VERSION_MAJOR/MINOR` if available, otherwise uses generic availability. It writes an emulated macro if another platform has already been detected; otherwise it becomes the active platform.

State and persistence behavior: Compile-time-only. Platform-detected state is shared with other Boost.Predef platform headers.

Dependencies and integration points: Included by the platform aggregator and complements the aggregate `mingw.h` and `mingw64.h` headers.

Risks: MinGW-w64 can define `__MINGW32__` for compatibility, so this macro may indicate the API family rather than exclusively a 32-bit binary target. Use with architecture macros for bitness.

Test signals: Declares primary and optional emulated Predef tests.
