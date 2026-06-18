# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_server.h

Purpose: Detects Windows Server UWP-family targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_SERVER`, `BOOST_PLAT_WINDOWS_SERVER_AVAILABLE`, and `BOOST_PLAT_WINDOWS_SERVER_NAME`.

Control flow: On Windows, if `WINAPI_FAMILY_SERVER` is defined and selected by `WINAPI_FAMILY`, the platform macro becomes available.

State and persistence behavior: Compile-time macro state only; successful detection includes `platform_detected.h`.

Dependencies and integration points: Relies on `windows_uwp.h` and Windows SDK family macros from `winapifamily.h`.

Risks: Depends on SDK support for `WINAPI_FAMILY_SERVER`; older SDKs cannot report it. It says nothing about runtime OS edition outside compile target family.

Test signals: Standard Boost.Predef generated test declaration.
