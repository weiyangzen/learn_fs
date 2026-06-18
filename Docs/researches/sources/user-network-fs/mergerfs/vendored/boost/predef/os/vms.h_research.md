# sources/user-network-fs/mergerfs/vendored/boost/predef/os/vms.h

Purpose: Detects OpenVMS/VMS as the active operating system for Boost.Predef.

Important APIs, types, and functions: Defines `BOOST_OS_VMS`, `BOOST_OS_VMS_AVAILABLE`, and `BOOST_OS_VMS_NAME`. If `__VMS_VER` exists, it converts that native version to Boost's numeric representation with `BOOST_PREDEF_MAKE_10_VVRR00PP00`.

Control flow: The macro starts as not available. If no prior OS detector has set `BOOST_PREDEF_DETAIL_OS_DETECTED` and either `VMS` or `__VMS` exists, the file sets `BOOST_OS_VMS` to the converted `__VMS_VER` or generic available value. A successful detection includes `boost/predef/detail/os_detected.h` to reserve the OS slot.

State and persistence behavior: Compile-time-only. The detection side effect is the shared OS-detected marker, preventing later OS headers from claiming the same compilation target.

Dependencies and integration points: Uses Boost.Predef version/make helpers and the test declaration header. It integrates with the one-OS selection convention used by `boost/predef/os.h`.

Risks: If another OS detector is included first and marks the target, VMS detection is suppressed. Version parsing depends on `__VMS_VER` keeping the expected decimal layout.

Test signals: `BOOST_PREDEF_DECLARE_TEST(BOOST_OS_VMS, BOOST_OS_VMS_NAME)` provides the generated-test hook.
