# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_desktop.h

Purpose: Detects Windows Desktop application targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_DESKTOP`, `BOOST_PLAT_WINDOWS_DESKTOP_AVAILABLE`, and `BOOST_PLAT_WINDOWS_DESKTOP_NAME`.

Control flow: If `BOOST_OS_WINDOWS` is true and either `WINAPI_FAMILY == WINAPI_FAMILY_DESKTOP_APP` or UWP support is unavailable, it marks desktop as available.

State and persistence behavior: Compile-time-only. Successful detection includes `platform_detected.h`.

Dependencies and integration points: Depends on Windows OS detection and `windows_uwp.h`. It provides a fallback for old SDKs lacking UWP family definitions.

Risks: The `!BOOST_PLAT_WINDOWS_UWP` fallback means old SDKs are assumed desktop. This is practical but can obscure newer Windows-family distinctions when SDK headers are incomplete.

Test signals: Declares a Boost.Predef generated test for the desktop macro.
