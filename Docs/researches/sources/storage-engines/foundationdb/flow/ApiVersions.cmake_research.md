# sources/storage-engines/foundationdb/flow/ApiVersions.cmake

## Purpose
`ApiVersions.cmake` is the authoritative CMake data file for FoundationDB API-version constants consumed by `ApiVersion.h.cmake`.

## Important APIs, Types, and Functions
It defines `FDB_AV_LATEST_VERSION`, `FDB_AV_LATEST_BINDINGS_VERSION`, and one `FDB_AV_*` variable per API feature, including snapshot RYW, persistent options, trace file identifiers, blob range APIs, tenant API milestones, total cost, tag throttled duration, future double/bool APIs, client status, and tenant id.

## Control Flow
The file is included by `flow/CMakeLists.txt`, which then runs `configure_file` to replace matching placeholders in `ApiVersion.h.cmake`. There is no procedural control flow beyond CMake `set` commands.

## State and Persistence Behavior
The file stores build-time constants only. Changing it changes generated headers and therefore compiled API-gating behavior.

## Dependencies and Integration Points
Its direct integration point is `FDB_API_VERSION_FILE` in `flow/CMakeLists.txt`. Bindings and client behavior depend on the generated constants being synchronized with released API semantics.

## Risks and Edge Cases
A wrong value can expose a feature to too-old API versions or hide it from versions that should support it. `LATEST_BINDINGS_VERSION` must remain compatible with language binding release expectations.

## Test Signals
Build success verifies placeholder availability. Behavioral tests for API-version-gated features provide indirect validation.
