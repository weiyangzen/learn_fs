# sources/user-network-fs/libsmb2/lib/CMakeLists.txt

## Purpose
`lib/CMakeLists.txt` assembles the libsmb2 library or platform-specific targets for CMake and ESP-IDF builds.

## Important APIs, Types, and Functions
It conditionally sets `KRB5_SOURCE`, defines source lists for `ESP_PLATFORM`, PS2 IOP/IRX, and normal builds, calls `register_component()` for ESP, creates `smb2_rpc`, `smb2man.irx`, `libsmb2` static Pico library, or normal `smb2` library targets, configures include directories, version/SOVERSION properties, Dreamcast VFS sources/install, `_U_` definitions, WindowsStore `_MSC_UWP`, and install rules.

## Control Flow
CMake evaluates platform variables, selects a source list, creates exactly the relevant target branch, adds definitions, and emits install rules unless excluded by platform conditions.

## State and Persistence Behavior
The file creates build-system state: targets, source membership, include paths, link libraries, install destinations, and post-build commands. No runtime persistence.

## Dependencies and Integration Points
It integrates with top-level CMake variables such as `GSSAPI_FOUND`, `LIBKRB5_FOUND`, `core_DEPENDS`, `CORE_LIBRARIES`, `PROJECT_VERSION`, `SOVERSION`, `INSTALL_INC_DIR`, `PICO_BOARD`, `ESP_PLATFORM`, `EE`, `IOP`, and `BUILD_IRX`.

## Risks and Edge Cases
The condition `if(NOT PICO_BOARD OR NOT ESP_PLATFORM)` is true for most combinations and may not express the intended "not Pico and not ESP" install gating. Header install lists omit `smb2-ioctl.h`. Source lists are duplicated across branches, so adding/removing a `.c` file requires multiple updates.

## Test Signals
Configure/build normal, ESP, Pico, PS2 IOP/IRX, Dreamcast, MSVC, and Kerberos-enabled builds. Inspect target source lists, install manifests, exported library names, and `_U_` definitions.
