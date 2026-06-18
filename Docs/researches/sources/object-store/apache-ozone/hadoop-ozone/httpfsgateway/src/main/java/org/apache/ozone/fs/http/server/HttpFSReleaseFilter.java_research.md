# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSReleaseFilter.java

## Purpose
`HttpFSReleaseFilter` returns per-request filesystem instances to the `FileSystemAccess` service after HTTP request completion.

## Important APIs, Types, and Functions
The class extends `FileSystemReleaseFilter` and overrides `getFileSystemAccess()` to return `HttpFSServerWebApp.get().get(FileSystemAccess.class)`.

## Control Flow
The parent filter owns request lifecycle behavior. This subclass supplies the HttpFS-specific service lookup used for release.

## State and Persistence Behavior
No state of its own. It participates in lifecycle cleanup of filesystem handles stored by `FileSystemReleaseFilter.setFileSystem()` in `HttpFSServer.createFileSystem()`.

## Dependencies and Integration Points
It integrates tightly with `HttpFSServer` streaming operations and the server webapp's service registry.

## Risks and Edge Cases
Correctness depends on the filter being installed in the webapp and on `HttpFSServerWebApp` being initialized. If missing, unmanaged filesystem instances used for streaming reads may leak.

## Test Signals
No direct test in this subset. Integration tests should assert filesystem release after streaming responses and failures.
