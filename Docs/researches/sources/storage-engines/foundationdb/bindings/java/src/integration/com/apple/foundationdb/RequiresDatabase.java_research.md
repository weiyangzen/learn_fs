# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RequiresDatabase.java

## Purpose
`RequiresDatabase` is a JUnit 5 extension that enables/skips integration tests based on `run.integration.tests` and performs a before-all health check against a running FoundationDB database.

## Important APIs, Types, and Functions
It implements `ExecutionCondition` and `BeforeAllCallback`. Key functions are `canRunIntegrationTest`, `evaluateExecutionCondition`, and `beforeAll`. It uses `FDB.selectAPIVersion`, optional `external_client_library` configuration, database options, transaction timeout, and JUnit `Assertions.fail`.

## Control Flow
`evaluateExecutionCondition` disables tests only when the system property `run.integration.tests` parses false. `beforeAll` selects FDB, sets external-client options once if configured, opens a database, and attempts up to ten small read transactions with a 5-second transaction timeout and 500 ms backoff. If all attempts fail, it fails the test class with a contextual message.

## State and Persistence Behavior
The static `networkOptionsSet` prevents repeated external-client option setup across classes. No database data is modified; the health check reads key `"test"`.

## Dependencies and Integration Points
It integrates with JUnit 5 extension APIs, Maven/JUnit configuration parameters, FoundationDB network option setup, and all annotated integration tests in this subset.

## Risks and Edge Cases
The condition message says "Database is running" whenever tests are enabled, before the health check actually proves it. `networkOptionsSet` is static and unsynchronized; parallel class initialization could race. Once external client options are set, later classes cannot change them. Missing `run.integration.tests` means tests run by default and fail if no cluster is available.

## Test Signals
Annotated tests get a consistent fail-fast connection check and optional external-client-library setup. A successful `beforeAll` means the Java binding can select the API, open a database, set timeout, and complete a read quickly.
