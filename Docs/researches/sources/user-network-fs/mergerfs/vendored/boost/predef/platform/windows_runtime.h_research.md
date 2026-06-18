# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_runtime.h

Purpose: Provides deprecated Windows Runtime detection for compatibility with older Boost.Predef users.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_RUNTIME`, `BOOST_PLAT_WINDOWS_RUNTIME_AVAILABLE`, and `BOOST_PLAT_WINDOWS_RUNTIME_NAME`.

Control flow: On Windows, it becomes available if either `BOOST_PLAT_WINDOWS_STORE` or `BOOST_PLAT_WINDOWS_PHONE` is available.

State and persistence behavior: Compile-time-only. Successful detection includes `platform_detected.h`.

Dependencies and integration points: Depends on `windows_phone.h` and `windows_store.h`. New code should use the specific Windows platform-family macros instead.

Risks: The header is explicitly deprecated and models an older UWP/runtime taxonomy. It may conflate distinct Store and Phone targets.

Test signals: Declares a generated test for `BOOST_PLAT_WINDOWS_RUNTIME`.
