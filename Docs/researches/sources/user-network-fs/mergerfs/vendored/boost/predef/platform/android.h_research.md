# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/android.h

Purpose: Detects Android as a platform layer.

Important APIs, types, and functions: Defines `BOOST_PLAT_ANDROID`, `BOOST_PLAT_ANDROID_AVAILABLE`, and `BOOST_PLAT_ANDROID_NAME`.

Control flow: Starts unavailable, then sets `BOOST_PLAT_ANDROID` to available when `__ANDROID__` is defined. Successful detection includes `platform_detected.h`.

State and persistence behavior: Compile-time-only. The platform-detected marker can influence later platform headers that support emulated-platform reporting.

Dependencies and integration points: Used by `endian.h` to choose `<endian.h>` on Android and by the `platform.h` aggregator.

Risks: Android also defines Linux-oriented macros in many toolchains, so OS and platform detectors should be interpreted together.

Test signals: Declares a generated Boost.Predef test for `BOOST_PLAT_ANDROID`.
