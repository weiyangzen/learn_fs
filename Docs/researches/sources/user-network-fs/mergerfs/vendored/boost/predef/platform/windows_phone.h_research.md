# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_phone.h

Purpose: Detects Windows Phone UWP-family targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_PHONE`, `BOOST_PLAT_WINDOWS_PHONE_AVAILABLE`, and `BOOST_PLAT_WINDOWS_PHONE_NAME`.

Control flow: On Windows, if `WINAPI_FAMILY_PHONE_APP` exists and `WINAPI_FAMILY` equals it, the macro becomes available and includes `platform_detected.h`.

State and persistence behavior: Compile-time-only. It participates in shared platform detection.

Dependencies and integration points: Depends on `windows_uwp.h` to include `winapifamily.h` when SDK support exists. The deprecated `windows_runtime.h` uses this macro.

Risks: Windows Phone family macros are SDK-era-specific and obsolete for modern Windows development, so absence does not imply a non-mobile app in all historical toolchains.

Test signals: Declares the generated Predef test.
