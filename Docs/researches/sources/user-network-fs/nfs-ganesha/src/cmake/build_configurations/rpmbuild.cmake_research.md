# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/rpmbuild.cmake

Purpose: RPM build preset placeholder that announces an RPM-oriented configuration.

Important APIs/types/functions: Emits `message(STATUS "Building RPM")`; it sets no feature variables itself.

Control flow: Included by external build selection; the top-level/default options and RPM packaging files carry the actual build behavior.

State and persistence behavior: No state beyond a CMake status message.

Dependencies and integration points: Depends entirely on surrounding RPM build scripts/spec logic and default options.

Risks: The comment says "Turn on everything" but the file does not set options, so it can be misleading and may not match RPM packager expectations.

Test signals: Compare RPM preset configure output and enabled options against the RPM spec or packaging policy.
