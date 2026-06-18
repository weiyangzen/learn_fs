<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/CMakeLists.txt -->
# Research: sources/storage-engines/foundationdb/packaging/msi/CMakeLists.txt

## Purpose
CMake wiring for producing a Windows MSI installer with WiX when WiX tools are available.

## Important APIs, Types, And Functions
Finds `WIX`, configures `FDBInstaller.wxs` through `generate_wxs.cmake`, compiles it with `candle`, links with `light`, and registers custom targets `wix_file`, `wixobj`, and `installer` under the global `packages` target.

## Control Flow
The flow substitutes target paths for `fdbserver`, `fdbcli`, `fdbbackup`, optional `fdbmonitor`, and `fdb_c`, generates the WiX source, builds the WiX object, then emits `foundationdb-<version>[-SNAPSHOT]-<arch>.msi` into the package directory.

## State And Persistence Behavior
Writes generated installer intermediates under the CMake binary directory and final MSI under `packages`. It does not install system state itself.

## Dependencies And Integration Points
Depends on CMake generator expressions, `FindWIX`, WiX `candle`/`light`, built FoundationDB binaries, C client library, Python binding target, and the WiX template. Integrates the Windows packaging target with normal build artifacts and the repo-level `packages` target.

## Risks And Edge Cases
If WiX is missing, packaging silently downgrades to a warning. Optional `fdbmonitor` handling must match the template; missing or malformed target paths break MSI generation late. The template dependency references both `.wxs` and `.wxs.cmake`, so stale generated files are possible if dependency names drift.

## Test Signals
Validation is by CMake configure/build of the `installer` target on Windows with WiX installed; no unit test exists.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/CMakeLists.txt -->
