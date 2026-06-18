# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FDBLibraryRule.java

## Purpose
`FDBLibraryRule` is a JUnit 5 extension that selects and preloads a FoundationDB API version before tests that need the native library or API singleton.

## Important APIs, Types, and Functions
The class implements `BeforeAllCallback`, stores an `apiVersion`, exposes `current()`, `v63()`, `get()`, and initializes `instance` in `beforeAll` by calling `FDB.selectAPIVersion`.

## Control Flow
Tests register the extension statically. Before all tests in the class, the extension selects the requested API version and stores the returned singleton-like `FDB` instance for later access.

## State and Persistence Behavior
The extension stores the selected `FDB` instance. Because FDB API selection is process-global/singleton-like, this can affect all later tests in the JVM.

## Dependencies and Integration Points
It depends on JUnit 5 extensions, `ApiVersion.LATEST`, and `FDB.selectAPIVersion`. It is used by tuple tests that require the API/library for versionstamp behavior.

## Risks and Edge Cases
Multiple test classes selecting different API versions in one JVM can conflict with the FDB singleton. The comment acknowledges the cache is only mildly useful because of that singleton behavior. There is no cleanup hook.

## Test Signals
Successful setup indicates the native library/API version can be selected before tuple or binding tests run.
