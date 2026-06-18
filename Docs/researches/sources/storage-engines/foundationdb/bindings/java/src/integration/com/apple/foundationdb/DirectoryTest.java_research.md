# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/DirectoryTest.java

## Purpose
`DirectoryTest` verifies basic Java directory-layer behavior against a running FoundationDB database: creation, subdirectory creation, moving, duplicate creation errors, and removal of missing directories.

## Important APIs, Types, and Functions
It uses `DirectoryLayer`, `DirectorySubspace`, `DirectoryAlreadyExistsException`, `NoSuchDirectoryException`, `Database.run`, and JUnit `@ExtendWith(RequiresDatabase.class)`.

## Control Flow
Each test opens a database with the latest API version and runs directory operations inside transactions. Creation tests create paths, inspect returned path metadata, and call `exists`. Move tests create source/destination paths and move a subdirectory with `moveTo`. Negative tests assert that duplicate creation and removing nonexistent paths produce the expected directory exceptions, allowing for exceptions wrapped in `CompletionException`.

## State and Persistence Behavior
Tests mutate the directory layer metadata in the default directory layer location. Most tests remove created paths in `finally`, but failures before cleanup or cleanup exceptions can leave directory metadata behind. The test does not isolate paths with UUID prefixes, so names like `foo`, `src`, and `dest` can collide with concurrent runs.

## Dependencies and Integration Points
It depends on a live FDB instance, `RequiresDatabase` health checking, Java directory-layer implementation, transaction retry behavior, and CompletableFuture exception wrapping.

## Risks and Edge Cases
The cleanup in `testCanCreateSubDirectory` removes the final path list after appending `"bar"`, so it removes `foo/bar` but may leave parent `foo` depending on directory-layer semantics. Tests sharing plain path names are brittle under parallel integration test execution. Catching both direct directory exceptions and `CompletionException` is useful but somewhat inconsistent across tests.

## Test Signals
Passing tests show the Java directory layer can create/open/move/remove metadata and preserve expected exception behavior against a real cluster.
