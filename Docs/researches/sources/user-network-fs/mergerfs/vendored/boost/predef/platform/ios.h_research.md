# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/ios.h

Purpose: Splits Apple's iOS OS detection into device and simulator platform categories.

Important APIs, types, and functions: Defines `BOOST_PLAT_IOS_DEVICE`, `BOOST_PLAT_IOS_DEVICE_AVAILABLE`, `BOOST_PLAT_IOS_DEVICE_NAME`, `BOOST_PLAT_IOS_SIMULATOR`, `BOOST_PLAT_IOS_SIMULATOR_AVAILABLE`, and `BOOST_PLAT_IOS_SIMULATOR_NAME`.

Control flow: If `BOOST_OS_IOS` is true, it includes `<TargetConditionals.h>`. `TARGET_OS_SIMULATOR == 1` or `TARGET_IPHONE_SIMULATOR == 1` selects simulator; otherwise it selects device.

State and persistence behavior: Compile-time-only. Successful device or simulator detection includes `platform_detected.h`.

Dependencies and integration points: Depends on `boost/predef/os/ios.h` for the OS-level Apple mobile target and on Apple's TargetConditionals header for simulator distinction.

Risks: The fallback treats any iOS target without simulator markers as device. SDK macro changes or non-Apple toolchains can affect precision.

Test signals: Declares separate generated tests for simulator and device macros.
