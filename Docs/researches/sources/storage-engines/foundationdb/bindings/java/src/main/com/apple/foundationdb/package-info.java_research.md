<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/package-info.java

## Purpose
This package descriptor documents the core Java FoundationDB API and encourages transaction retry-loop helpers.

## Important APIs, Types, And Functions
It references `Database`, `TransactionContext.run`, `TransactionContext.runAsync`, `Transaction.commit`, and transaction developer documentation. There is no executable API in this file.

## Control Flow, State, And Persistence
The documented control flow is that clients should run work inside binding-managed retry loops so database commits complete successfully before the outer call returns.

## Dependencies And Integration Points
The file is integrated with Javadoc for the root `com.apple.foundationdb` package and contextualizes directory, tuple, and subspace layers.

## Risks And Test Signals
Documentation can drift as API-version or retry-loop guidance changes. Direct test signals are compilation and generated docs; behavior is tested through the referenced classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/package-info.java -->
