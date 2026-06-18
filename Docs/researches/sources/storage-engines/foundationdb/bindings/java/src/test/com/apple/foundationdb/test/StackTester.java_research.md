# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackTester.java

Purpose: synchronous cross-binding stack-machine executor for the Java binding. It is the blocking counterpart to `AsyncStackTester` and exercises broad FoundationDB API behavior from tuple-encoded instructions stored in the database.

Important APIs and flow: `processInstruction` dispatches stack, transaction, mutation, read, range, key selector, version, tuple, error, and unit-test operations, usually blocking with `join`/`get`. `SynchronousContext` scans instruction keys under the prefix and delegates `DIRECTORY_` commands to `DirectoryExtension`. Helpers execute retry-wrapped mutations, filter `getKey` results, read ranges by iterator or `asList`, log stack state, and run watch/locality smoke tests during `UNIT_TESTS`.

State and persistence: uses `Context` for shared stack, transaction registry, child contexts, and `lastVersion`. It persists tested mutations and stack logs; unit tests may set options and exercise watches/locality. Risks include broad `catch` converting only FDB failures to stack errors, random choice between iterator and list range paths, blocking waits that can hang on unresolved futures, and destructive operations driven by input scripts. Test signal is high for cross-binding parity, especially synchronous behavior.
