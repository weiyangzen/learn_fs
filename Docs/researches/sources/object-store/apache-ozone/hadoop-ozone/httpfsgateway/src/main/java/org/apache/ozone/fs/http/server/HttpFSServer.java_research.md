# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSServer.java

## Purpose
`HttpFSServer` is the Jersey JAX-RS resource that exposes WebHDFS-style HTTP endpoints under `/webhdfs/v1`. It parses operations and parameters, enforces gateway access mode, executes filesystem commands, builds HTTP responses, and writes audit context.

## Important APIs, Types, and Functions
The class is annotated `@Path(HttpFSConstants.SERVICE_VERSION)`. Public handlers cover GET, PUT, POST, DELETE, and root variants. Private helpers include `getParams()`, `fsExecute()`, `createFileSystem()`, `makeAbsolute()`, upload/open redirection URL builders, and one `handle*` method per supported operation. `AccessMode` supports `READWRITE`, `WRITEONLY`, and `READONLY`.

## Control Flow
Each HTTP method gets the authenticated `UserGroupInformation`, parses parameters via `HttpFSParametersProvider`, normalizes the path to an absolute path, records operation/host in MDC, and switches on `op`. Handlers create `FSOperations` executors and call `fsExecute()`, except streaming `OPEN`, which creates an unmanaged filesystem registered for release and wraps the returned stream in `InputStreamEntity`. Create and append implement the WebHDFS two-step upload flow using temporary redirects unless `data=true` or `noredirect=true`.

## State and Persistence Behavior
The server instance holds only `accessMode`, read from `httpfs.access.mode`. Persistent filesystem state changes occur through `FSOperations`. Request-scoped filesystem handles for streaming are stored in `FileSystemReleaseFilter`.

## Dependencies and Integration Points
It integrates Jersey annotations, servlet request context, Hadoop UGI, HttpFS auth identity, `FileSystemAccess`, `Groups`, `Instrumentation`, `InputStreamEntity`, `HttpFSParametersProvider`, `HttpFSConstants`, and `HttpFSExceptionProvider`. It depends on `HttpFSServerWebApp` for configuration and services.

## Risks and Edge Cases
Several declared operations are intentionally unsupported and throw `UnsupportedOperationException` despite being present in constants and parameter definitions. Read-only mode blocks all PUT/POST/DELETE; write-only mode permits only `GETFILESTATUS` and `LISTSTATUS`. The `noredirect` handling returns a JSON `Location` rather than issuing a redirect. Streaming open handles interruption by logging and restoring interrupt status but may leave `is` null if interrupted.

## Test Signals
No direct server tests are included in this subset. High-value tests would cover operation routing, access-mode gates, upload redirect variants, unsupported operations, auth user propagation, audit MDC, and exception mapping.
