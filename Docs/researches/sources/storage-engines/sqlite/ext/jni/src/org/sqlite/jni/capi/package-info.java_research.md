# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/package-info.java

## Purpose
`package-info.java` documents the `org.sqlite.jni.capi` package: a JNI binding intended to map SQLite's C API into Java with minimal abstraction.

## Important APIs, Types, and Functions
The package's primary API surface is `CApi`. The documentation describes goals: near 1-to-1 C API mapping, C documentation reuse, Java 8 support, environment independence, and no third-party dependencies.

## Control Flow
There is no runtime control flow. The file supplies package-level Javadoc and package declaration.

## State and Persistence Behavior
No runtime state exists. The documentation defines expected handle/threading semantics for the package.

## Dependencies and Integration Points
It links to `org.sqlite.jni.capi.CApi` and SQLite C API docs. It frames the relationship between low-level bindings and optional client-created higher-level wrappers.

## Risks
Important risk guidance is in threading notes: Java-facing SQLite handles and database-specific resources must not be used concurrently from multiple threads, even if SQLite itself is thread-safe. Mixed Java/C native use can bypass proxy bookkeeping and break callback/resource management.

## Test Signals
`Tester1` operationalizes these guarantees by exercising thread modes, handle invalidation, callback proxies, and no-third-party low-level usage.
