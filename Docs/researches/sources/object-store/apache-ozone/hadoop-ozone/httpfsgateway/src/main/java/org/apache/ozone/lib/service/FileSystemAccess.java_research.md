# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccess.java

## Purpose
`FileSystemAccess` defines the service API for authenticated Hadoop `FileSystem` access from HttpFS request handlers.

## Important APIs, types, and functions
`FileSystemExecutor<T>` encapsulates a filesystem operation. `execute(user, conf, executor)` runs managed operations. `createFileSystem(user, conf)` and `releaseFileSystem(fs)` expose unmanaged lifecycle control for streaming responses. `getFileSystemConfiguration()` returns a service-created configuration template.

## Control flow
The interface separates short managed operations from request-spanning filesystem handles that must be released later.

## State and persistence behavior
The interface owns no state. Implementations cache or count filesystem instances.

## Dependencies and integration points
`FileSystemAccessService` implements it. `FileSystemReleaseFilter` releases unmanaged handles after servlet processing.

## Risks and edge cases
Callers using `createFileSystem` must always call `releaseFileSystem`; otherwise cached filesystem counts and resources can leak.

## Test signals
`TestHttpFSMetrics` invokes `execute` with `FSCreate` and `FSAppend` operations through a mocked implementation.
