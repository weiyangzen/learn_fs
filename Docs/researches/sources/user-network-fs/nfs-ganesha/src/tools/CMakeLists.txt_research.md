# sources/user-network-fs/nfs-ganesha/src/tools/CMakeLists.txt

Purpose: top-level tools build entry point.

Important APIs, types, and functions: conditionally calls `add_subdirectory(multilock)` when `USE_TOOL_MULTILOCK` is enabled.

Control flow: there is no executable declaration in this file except the conditional subdirectory inclusion.

State and persistence: build graph only.

Dependencies and integration points: integrates with the `multilock` CMake subtree and the project option `USE_TOOL_MULTILOCK`.

Risks: tools present in this directory, such as scripts or RADOS utilities, may be built/installed elsewhere or not represented here. Enabling multilock depends entirely on the CMake option.

Test signals: build configuration can verify that toggling `USE_TOOL_MULTILOCK` includes or excludes the subdirectory.
