# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCaps.cmake

Purpose: Finds Linux capabilities support through libcap and `sys/capability.h`.

Important APIs/types/functions: Consumes `CAPS_PREFIX`; finds library `cap` into `CAPS`, checks `cap_set_proc` into `HAVE_SET_PROC`, finds `CAPS_INCLUDE_DIR`, and sets `CAPS_LIBRARIES` only when the function check passes.

Control flow: Library symbol availability gates the final library variable, then `find_package_handle_standard_args` requires both `CAPS_LIBRARIES` and include dir.

State and persistence behavior: CMake cache/check variables only.

Dependencies and integration points: Used by privilege/capability handling code that needs libcap.

Risks: `check_library_exists(cap cap_set_proc "" HAVE_SET_PROC)` does not use the found `CAPS` path, so custom prefixes may fail symbol checks if not on default linker paths. The intermediate library variable is named `CAPS`, while consumers likely use `CAPS_LIBRARIES`.

Test signals: Configure with system libcap, custom prefix, header-only missing lib, and lib path not in default linker search.
