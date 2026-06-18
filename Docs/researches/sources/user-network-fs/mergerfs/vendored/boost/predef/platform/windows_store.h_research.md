# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_store.h

Purpose: Detects Windows Store application targeting.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_STORE`, `BOOST_PLAT_WINDOWS_STORE_AVAILABLE`, and `BOOST_PLAT_WINDOWS_STORE_NAME`.

Control flow: On Windows, it checks `WINAPI_FAMILY_PC_APP` and deprecated `WINAPI_FAMILY_APP` against `WINAPI_FAMILY`. A match sets the macro to available and includes `platform_detected.h`.

State and persistence behavior: Compile-time-only.

Dependencies and integration points: Depends on `windows_uwp.h` for SDK family support. `windows_runtime.h` uses this macro as one of its deprecated runtime inputs.

Risks: Includes a deprecated family macro for compatibility; consumers should understand which SDK family is actually being targeted.

Test signals: Declares the generated test for the Store macro.
