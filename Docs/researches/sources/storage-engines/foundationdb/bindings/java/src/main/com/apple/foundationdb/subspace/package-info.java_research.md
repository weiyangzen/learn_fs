<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/package-info.java

## Purpose
This package descriptor documents subspaces as tuple-prefixed namespaces for application data.

## Important APIs, Types, And Functions
It exports package Javadoc only and points users toward `Subspace` and developer-guide sub-keyspace documentation.

## Control Flow, State, And Persistence
No code executes here. The documented persistence model is that packed tuple keys share a prefix and unpacking removes that prefix.

## Dependencies And Integration Points
The descriptor supports generated documentation for `com.apple.foundationdb.subspace`, which is used by directory and tuple APIs.

## Risks And Test Signals
Documentation drift is the primary risk. Direct validation is limited to Javadoc generation; behavioral tests belong to `Subspace` and directory integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/package-info.java -->
