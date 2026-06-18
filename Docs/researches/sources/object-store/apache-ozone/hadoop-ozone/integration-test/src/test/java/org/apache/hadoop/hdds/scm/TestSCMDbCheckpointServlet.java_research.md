# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDbCheckpointServlet.java

## Purpose

`TestSCMDbCheckpointServlet` tests SCM DB checkpoint download servlet behavior for supported HTTP methods, excluded file handling, and invalid POST content type. It protects the HTTP checkpoint endpoint used for snapshot/checkpoint transfer.

## Important APIs, Types, And Functions

The class uses `SCMDbCheckpointServlet`, `DBCheckpoint`, servlet request/response mocks, `@ParameterizedTest` with `getHttpMethods`, and helper methods `setupHttpMethod`, `setupPostMethod`, `setupGetMethod`, and `doEndpoint`. It writes response output to a temporary file through a custom `ServletOutputStream`.

## Control Flow

Setup starts a MiniOzoneCluster and captures the SCM checkpoint servlet dependencies. Parameterized tests configure GET or POST request mocks, invoke the endpoint, and inspect the generated archive/output while excluding selected files. The invalid POST test asserts rejection of an unsupported content type.

## State And Persistence Behavior

The servlet snapshots SCM metadata into checkpoint files and streams archive bytes to HTTP responses. The test reads temporary output archives but does not intentionally mutate SCM logical state.

## Dependencies And Integration Points

It integrates SCM metadata store checkpointing, HTTP servlet request/response handling, archive generation, and checkpoint exclusion lists.

## Risks And Test Signals

Failures indicate broken DB checkpoint streaming, incorrect method/content-type handling, resource leaks in output streams, or archive content drift. The endpoint is operationally sensitive because followers and admins depend on checkpoint downloads.
