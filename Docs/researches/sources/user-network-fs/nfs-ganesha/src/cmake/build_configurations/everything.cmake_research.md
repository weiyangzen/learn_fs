# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/everything.cmake

Purpose: Broad feature preset intended to enable most optional build paths.

Important APIs/types/functions: Enables `PROXYV4_HANDLE_MAPPING`, `USE_DBUS`, `USE_CB_SIMULATOR`, `USE_FSAL_XFS`, `USE_FSAL_CEPH`, `USE_FSAL_RGW`, `USE_FSAL_GLUSTER`, and `USE_TOOL_MULTILOCK`.

Control flow: These variables are consumed by later option tests, dependency discovery, and target inclusion, making this a high-dependency configure mode.

State and persistence behavior: CMake configuration state only.

Dependencies and integration points: Pulls in optional FSALs, DBus, callback simulator, and multilock tool integration. It relies on the relevant `Find*.cmake` modules to locate dependencies or disable/fail features.

Risks: "Everything" is not exhaustive if newer options are added. It can expose dependency skew and optional API compatibility issues, especially Ceph/RGW/Gluster/XFS.

Test signals: Full dependency CI configure, package build, and smoke tests for all enabled FSAL/tool targets.
