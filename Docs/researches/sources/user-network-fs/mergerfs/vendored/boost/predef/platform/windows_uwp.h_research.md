# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/windows_uwp.h

Purpose: Detects whether the Windows build environment can target Universal Windows Platform families and records the Windows SDK build version.

Important APIs, types, and functions: Defines `BOOST_PLAT_WINDOWS_UWP`, `BOOST_PLAT_WINDOWS_UWP_AVAILABLE`, `BOOST_PLAT_WINDOWS_UWP_NAME`, and `BOOST_PLAT_WINDOWS_SDK_VERSION`.

Control flow: On Windows, non-MinGW32, non-WinCE, non-Wine builds include `<ntverp.h>` and convert `VER_PRODUCTBUILD` to a Boost version. UWP is available when the SDK build is at least 9200 or when MinGW-w64 major version is at least 3. If available, it includes `platform_detected.h` and `<winapifamily.h>`.

State and persistence behavior: Compile-time-only. It also exposes SDK version state to dependent Windows platform-family headers.

Dependencies and integration points: Central dependency for Windows Desktop, Store, Phone, Server, System, and Runtime detectors.

Risks: Header inclusion is conditional to avoid missing `ntverp.h` on some toolchains. SDK version availability does not mean a particular family is selected; it only means family targeting support exists.

Test signals: Declares a generated Predef test for UWP.
