<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/versions.target.cmake -->
# sources/storage-engines/foundationdb/versions.target.cmake

## Purpose
CMake fragment listing FoundationDB restart/upgrade target versions used by build or test orchestration.

## Important APIs, Types, And Functions
Defines `FDB_RESTARTER_VERSION_LIST` with values parsed from `set(...)`: <?xml version="1.0"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <Version>${FDB_VERSION}</Version>
    <PackageName>${FDB_MAJOR}.${FDB_MINOR}</PackageName>
  </PropertyGroup>
</Project>.

## Control Flow
No runtime control flow. CMake evaluates this file and exposes the version list to callers that generate restart/upgrade tests or targets.

## State And Persistence Behavior
No persistent state beyond the configured CMake variable in the build directory.

## Dependencies And Integration Points
Integrated with FoundationDB CMake logic that consumes restart target versions, especially upgrade/restarting test generation.

## Risks
The version list must stay aligned with available restart fixtures and supported upgrade paths; stale values can generate missing or irrelevant test targets.

## Test Signals
CMake configure/generation and restart test target discovery are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/versions.target.cmake -->
