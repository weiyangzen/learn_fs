# sources/user-network-fs/mergerfs/vendored/boost/predef/platform.h

Purpose: Aggregates Boost.Predef platform-family detectors.

Important APIs, types, and functions: It defines no standalone macros, but includes platform detectors for Android, CloudABI, MinGW variants, Windows UWP/families, deprecated Windows Runtime, and iOS device/simulator.

Control flow: A normal include guard is combined with `BOOST_PREDEF_INTERNAL_GENERATE_TESTS`, allowing test-generation passes to re-enter included headers.

State and persistence behavior: No runtime state. Inclusion updates compile-time platform-detection macro state through child headers and `platform_detected.h`.

Dependencies and integration points: Used by `boost/predef.h` and consumers that need platform categories separate from OS detection. Windows-specific child headers depend on `BOOST_OS_WINDOWS` and each other.

Risks: Include order matters for platform emulation markers because some child headers define `*_EMULATED` when another platform has already claimed detection. Aggregating all platform headers is convenient but can expose multiple related Windows-family macros.

Test signals: Each included child detector declares its own generated Predef test.
