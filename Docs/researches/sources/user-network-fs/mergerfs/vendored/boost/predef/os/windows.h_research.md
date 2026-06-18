# sources/user-network-fs/mergerfs/vendored/boost/predef/os/windows.h

Purpose: Detects Microsoft Windows as the active operating system for Boost.Predef.

Important APIs, types, and functions: Defines `BOOST_OS_WINDOWS`, `BOOST_OS_WINDOWS_AVAILABLE`, and `BOOST_OS_WINDOWS_NAME`.

Control flow: The detector starts with `BOOST_VERSION_NUMBER_NOT_AVAILABLE`. If no previous OS was detected and `_WIN32`, `_WIN64`, `__WIN32__`, `__TOS_WIN__`, or `__WINDOWS__` is defined, it sets `BOOST_OS_WINDOWS` to `BOOST_VERSION_NUMBER_AVAILABLE` and includes `os_detected.h`.

State and persistence behavior: No runtime state. The only state is preprocessor state, especially the shared `BOOST_PREDEF_DETAIL_OS_DETECTED` marker that serializes OS detection.

Dependencies and integration points: Uses Boost.Predef version/make support and generated test hooks. Windows platform-family headers such as `windows_uwp.h` and `windows_desktop.h` depend on this macro before making finer-grained platform decisions.

Risks: The macro reports the Windows OS but not SDK family, desktop/UWP capabilities, or MinGW flavor. Consumers must combine it with platform detectors for those distinctions.

Test signals: The declared Predef test checks the final `BOOST_OS_WINDOWS` value in Boost's generated test mode.
