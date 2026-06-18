# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSExceptionProvider.java

## Purpose
`HttpFSExceptionProvider` maps exceptions thrown by HttpFS request handling to HTTP responses and logs failures in both audit and service logs.

## Important APIs, Types, and Functions
The class extends `org.apache.ozone.lib.wsrs.ExceptionProvider` and is a JAX-RS `@Provider`. `toResponse(Throwable)` unwraps `FileSystemAccessException` and `ContainerException`, maps security failures to 401, missing files to 404, IO and unknown failures to 500, unsupported operations and illegal arguments to 400, and delegates response body creation to `createResponse()`. `log()` writes audit and service warnings using MDC method/path data. `logErrorFully()` logs debug stack detail for server/bad-request categories.

## Control Flow
When Jersey catches an exception, it invokes `toResponse()`. Mapping occurs before the base provider creates the response; logging uses the overridden `log()` hook.

## State and Persistence Behavior
No persistent state. Side effects are logs only.

## Dependencies and Integration Points
It integrates with JAX-RS exception mapping, Ozone `FileSystemAccessException`, SCM `ContainerException`, SLF4J/MDC, and the shared base exception provider.

## Risks and Edge Cases
Unwrapping assumes meaningful causes. IOExceptions are reported as 500 rather than more granular client/server errors. Audit logging depends on request handlers populating MDC values.

## Test Signals
No direct test in this subset. Unit tests should cover each mapping branch and logging with missing MDC data.
