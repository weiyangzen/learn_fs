# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/test/java/org/apache/ozone/fs/http/server/metrics/TestHttpFSMetrics.java

## Purpose
`TestHttpFSMetrics` verifies that HttpFS create and append operations increment operation counters and written-byte metrics.

## Important APIs, types, and functions
The suite uses `HttpFSServerWebApp`, `HttpFSServerMetrics`, `FileSystemAccess`, `FileSystemAccessService`, `FSOperations.FSCreate`, and `FSOperations.FSAppend`. `MockFileSystemAccessService` overrides `createFileSystem` and `closeFileSystem` to use a mocked Hadoop `FileSystem`.

## Control flow
`@BeforeAll` creates temp home/log/conf/temp directories and sets `httpfs.home.dir`. `@BeforeEach` creates a service-created `Configuration`, initializes the web app, replaces filesystem access with the mock service, obtains metrics, and creates a test UGI. Tests stub `mockFs.create` or `mockFs.append`, execute the corresponding FS operation through `fsAccess.execute`, and assert metric increments.

## State and persistence behavior
The server lifecycle and metrics are in-memory. Temporary directories satisfy server directory validation. No real filesystem data is written because the Hadoop filesystem is mocked.

## Dependencies and integration points
This test covers the integration between server boot, service replacement, filesystem execution, FS operation implementations, and metrics counters.

## Risks and edge cases
Static mocks are shared across tests; stubbing interactions must remain isolated. The test shuts metrics down and destroys the singleton web app after each test.

## Test signals
Signals are exact increments: create/append operation counters increase by one and bytes-written increases by four for the `"test"` input.
