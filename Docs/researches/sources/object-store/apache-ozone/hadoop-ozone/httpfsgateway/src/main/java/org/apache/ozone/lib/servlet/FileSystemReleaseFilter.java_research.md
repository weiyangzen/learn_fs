# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/FileSystemReleaseFilter.java

## Purpose
`FileSystemReleaseFilter` guarantees that request-scoped unmanaged `FileSystem` instances are returned to `FileSystemAccess` after servlet processing, especially for streaming responses.

## Important APIs, types, and functions
It implements `Filter`, keeps a static thread-local `FileSystem`, exposes `setFileSystem(fs)`, and requires subclasses to implement `getFileSystemAccess()`.

## Control flow
`doFilter()` delegates to the chain in a try block, then in finally checks the thread-local, removes it, and calls `releaseFileSystem(fs)`.

## State and persistence behavior
State is a per-thread filesystem reference. No durable state is written.

## Dependencies and integration points
`HttpFSReleaseFilter` is the concrete gateway subclass. `FileSystemAccessService.createFileSystem` increments unmanaged count, and this filter should call release at request completion.

## Risks and edge cases
If streaming occurs on a different thread than the request filter thread, the thread-local release mechanism can miss the handle. If release throws, it propagates from the finally block.

## Test signals
No direct tests in this subset. Streaming read tests and unmanaged filesystem counters would reveal leaks.
