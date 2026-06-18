# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_system.h

Purpose: Detects Windows System, drivers, and tools targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_SYSTEM`, `BOOST_PLAT_WINDOWS_SYSTEM_AVAILABLE`, and `BOOST_PLAT_WINDOWS_SYSTEM_NAME`.

Control flow: On Windows, if `WINAPI_FAMILY_SYSTEM` is defined and selected by `WINAPI_FAMILY`, it marks the system platform as available.

State and persistence behavior: Compile-time-only. Successful detection writes the platform-detected marker.

Dependencies and integration points: Depends on `windows_uwp.h` and Windows SDK family macros.

Risks: This is a compile-target family detector, not a runtime capability probe. Missing SDK macros leave it unavailable.

Test signals: Declares the standard generated Predef test.
