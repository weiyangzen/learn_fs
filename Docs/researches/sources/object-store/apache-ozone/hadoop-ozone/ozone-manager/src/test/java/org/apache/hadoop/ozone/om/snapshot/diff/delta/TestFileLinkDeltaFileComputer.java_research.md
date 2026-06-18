# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFileLinkDeltaFileComputer.java

## Purpose
`TestFileLinkDeltaFileComputer` validates the abstract base behavior for delta-file computers that materialize hard links into a temporary delta directory. It uses a concrete inner subclass to expose protected behavior and stub `computeDeltaFiles`.

## Important APIs, Types, and Functions
- `FileLinkDeltaFileComputer` supplies delta-directory lifecycle, hard-link creation, snapshot/local-data accessors, activity updates, and public `getDeltaFiles`.
- `TestableFileLinkDeltaFileComputer` overrides `computeDeltaFiles` and allows tests to inject an `Optional<Map<Path, Pair<Path, SstFileInfo>>>`.
- `createLink(Path)` creates unique hard links under the delta directory while preserving source file extensions.
- `getDeltaFiles(...)` fetches `TablePrefixInfo` from the active metadata manager and converts the internal map to a collection of `(deltaPath, SstFileInfo)` pairs.

## Control Flow
Constructor tests assert that a missing or existing delta directory is handled. Link tests create real files, then verify link existence, extension preservation, content visibility, unique naming across multiple links, and retry behavior when a next numeric link name already exists. Accessor tests validate delegation to `OmSnapshotLocalDataManager.getOmSnapshotLocalData`, `OmSnapshotManager.getActiveSnapshot`, and `getActiveMetadataManager`. `getDeltaFiles` tests assert success when the abstract compute method returns a map and `IOException` when it returns `Optional.empty()`.

## State and Persistence Behavior
The class creates and deletes a filesystem directory under `@TempDir`. The tests verify that `close()` removes the directory both when empty and when populated with links, and that closing a missing directory is harmless. Hard-link tests imply shared persistence with source files: content written to the source is visible through the link.

## Dependencies and Integration Points
The base class depends on OM snapshot manager APIs, active metadata table prefix calculation, snapshot local data providers, and `SstFileInfo` metadata. The activity reporter bridges file-link delta work to snapshot diff progress reporting through `SubStatus`.

## Risks and Edge Cases
Covered risks include name collisions in concurrent link creation, leaking temporary delta directories, treating absent delta computation as success, and extension loss. The tests do not verify cross-filesystem hard-link failure behavior, permissions errors, or cleanup failure handling.

## Test Signals
This file provides the foundational contract for the concrete diff computers: any successful diff returns linked files under a managed delta directory, and failure is represented by an absent optional that `getDeltaFiles` converts to `IOException`.
