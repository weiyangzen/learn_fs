<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/scripts/CMakeLists.txt

## Purpose
This CMake file conditionally includes admin-tool script subdirectories in the build.

## Important APIs, Types, and Functions
It checks `USE_ADMIN_TOOLS` and, when enabled, calls `add_subdirectory(ganeshactl)`, `add_subdirectory(gpfs-epoch)`, and `add_subdirectory(ganesha-top)`.

## Control Flow
The whole file is a single build-time conditional. If admin tools are disabled, no script subdirectories are added from here.

## State and Persistence Behavior
It affects generated build-system state and install targets from child directories. It has no runtime state.

## Dependencies and Integration Points
It depends on the top-level `USE_ADMIN_TOOLS` CMake option and the presence of the three child directories. Packaging in the RPM spec uses the same admin-tools concept through `%{with utils}`/`-DUSE_ADMIN_TOOLS`.

## Risks and Edge Cases
All three tools are tied to one option; there is no per-tool selection here. Missing child directories or child CMake errors break admin-tool builds. Packaging must stay aligned with what these subdirectories install.

## Test Signals
Configure/build tests should run with `USE_ADMIN_TOOLS=ON` and `OFF`, verifying child targets and installed scripts are present only when expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/CMakeLists.txt -->
