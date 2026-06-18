# `sources/storage-engines/foundationdb/fdbserver/datadistributor/CMakeLists.txt`

## Purpose

This CMake file defines the datadistributor sublibrary and its local tests. It collects all sources in the directory, builds them as a static Flow target named `fdbserver_datadistributor`, wires link and unit tests, and exposes the datadistributor include path to downstream targets.

## Important Build APIs

- `fdb_find_sources(FDBSERVER_DATADISTRIBUTOR_SRCS)` discovers source files under this directory according to FoundationDB's build helpers.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_datadistributor SRCS ...)` creates the static library target.
- `add_fdbserver_link_test(fdbserver_datadistributorlinktest fdbserver_datadistributor fdbserver_core)` ensures the datadistributor library links with core server code.
- `add_fdbserver_unit_test(fdbserver_datadistributor_test datadistributor fdbserver_datadistributor fdbserver_core)` creates the unit-test executable/category that picks up `TEST_CASE` registrations such as `AuditUtilsTests.cpp`, `DDRelocationQueue.actor.cpp`, and `DDShardTracker.cpp`.
- `configure_fdbserver_common_includes()`, `target_include_directories()`, and `target_link_libraries()` apply include and dependency wiring.

## Control Flow

The file is declarative. Source discovery runs first, then target creation, test target creation, include configuration, and final private linkage to `fdbserver_core`. The include directories are split between a public `${CMAKE_CURRENT_SOURCE_DIR}/include` path for exported datadistributor headers and a private current-source path for implementation-local headers such as `DDRelocationQueue.h`.

## State and Persistence Behavior

There is no runtime state. The build state it influences is target graph metadata: source membership, include search paths, static-library artifacts, and test executables. Since `fdb_find_sources()` is directory driven, adding or removing source files in this folder changes the library/test composition without needing explicit per-file edits here.

## Dependencies and Integration Points

The target links privately against `fdbserver_core`, while tests link both `fdbserver_datadistributor` and `fdbserver_core`. The public include directory lets other server code include headers under `fdbserver/datadistributor/...`. The private current-source include path supports local implementation includes like `"DDRelocationQueue.h"` without exporting that path as API.

## Risks and Edge Cases

Directory-wide source discovery is convenient but can accidentally compile experimental or generated files if they are placed under the source folder and match the helper's filters. Any missing dependency in `target_link_libraries()` may show up only in link tests or downstream targets. Public/private include separation is important: moving a header from `include/` to the implementation folder, or vice versa, changes what external targets can include.

## Test Signals

The file creates both a link test and unit-test target. The link test catches unresolved symbols and target dependency mistakes. The unit target provides the execution surface for Flow `TEST_CASE`s in this directory; failures in audit, queue, or tracker unit cases should be attributable through the `datadistributor` test category.
