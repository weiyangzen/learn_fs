# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/debian.cmake

Purpose: Debian package-oriented preset that enables DBus and admin tools for a DPKG build.

Important APIs/types/functions: Sets `USE_DBUS ON`, `USE_ADMIN_TOOLS ON`, and emits `Building DPKG`.

Control flow: Included during configure before dependent package and subdirectory logic evaluate these options.

State and persistence behavior: CMake configuration variables only.

Dependencies and integration points: Enables DBus/admin-tool build paths, implying later discovery of DBus-related dependencies and inclusion of admin utilities.

Risks: It does not force package generator selection itself; packaging behavior depends on surrounding CPack/debian logic. Missing DBus dependencies can make this preset fail or disable functionality depending on option-required handling.

Test signals: Configure a Debian packaging build and verify admin tools and DBus-dependent targets are present.
