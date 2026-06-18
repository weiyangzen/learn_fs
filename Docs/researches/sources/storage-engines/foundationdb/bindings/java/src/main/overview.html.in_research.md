<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/overview.html.in -->
# sources/storage-engines/foundationdb/bindings/java/src/main/overview.html.in

## Purpose
This Javadoc overview introduces the Java binding, installation, basic usage, and the included Tuple and Directory APIs.

## Important APIs, Types, And Functions
The HTML references client binaries, Maven Central artifact `org.foundationdb:fdb-java`, `FDB.selectAPIVersion(ApiVersion.LATEST)`, `Database`, `Transaction`, `Tuple`, and directory/subspace APIs. It includes a runnable-style example that opens the default database and writes/reads a tuple key.

## Control Flow, State, And Persistence
The example selects an API version, opens a database, runs a transaction that sets key `Tuple.from("hello").pack()` to value `Tuple.from("world").pack()`, then runs a second transaction to read and unpack it.

## Dependencies And Integration Points
This file feeds generated Java documentation and links to FoundationDB docs for client installation, cluster files, tuple data modeling, and directory usage.

## Risks And Test Signals
Risks include stale supported API version range, outdated Maven URL/artifact, example imports drifting, and links moving. Direct tests are documentation build checks and example compilation/smoke tests against a running cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/overview.html.in -->
