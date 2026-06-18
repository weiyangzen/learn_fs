# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTaskStatusService.java

## Purpose
Tests that `TaskStatusService.getTaskStats` returns rows from the Recon task status SQL table without altering key status fields.

## Important APIs, Types, And Functions
The file uses `TaskStatusService`, `AbstractReconSqlDBTest`, Guice child injector binding, `ReconTaskStatusDao`, `ReconTaskStatus`, JAX-RS `Response`, and a parameterized JUnit test over `lastTaskRunStatus` values `0`, `1`, and `-1`.

## Control Flow
`setUp` creates a child injector and binds a new `TaskStatusService` instance. The parameterized test inserts one `ReconTaskStatus` record into the DAO, invokes `getTaskStats`, casts the response entity to a list, and compares task name, last-updated timestamp, last run status, and current-running flag.

## State And Persistence
State is stored in the in-memory/test SQL database provided by `AbstractReconSqlDBTest`. The only persisted row per invocation is a `Dummy_Task` record with current timestamp and the parameterized status value.

## Dependencies And Integration Points
The test validates the service’s integration with generated jOOQ DAO/POJO classes under `org.apache.ozone.recon.schema.generated`. It also confirms Guice injection can provide the service in the Recon SQL test harness.

## Risks
The test does not assert response status code or ordering beyond a single row. It covers status value preservation but not multiple tasks, empty table behavior, or running-task flag variations.

## Test Signals
The signal is successful round-trip retrieval of inserted task status rows for success, failure, and unknown-like numeric task statuses.
