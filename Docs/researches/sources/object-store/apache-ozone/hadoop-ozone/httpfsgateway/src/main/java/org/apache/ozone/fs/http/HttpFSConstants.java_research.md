# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/HttpFSConstants.java

## Purpose
`HttpFSConstants` centralizes protocol constants for the Ozone HttpFS/WebHDFS-compatible server: HTTP methods, query parameter names, JSON field names, service paths, upload content type, and supported operations.

## Important APIs, Types, and Functions
The interface defines constants such as `SCHEME`, `OP_PARAM`, `SERVICE_PATH`, JSON response keys for statuses/checksums/ACLs/xattrs/quota/storage policies, and `UPLOAD_CONTENT_TYPE`. `permissionToString(FsPermission)` serializes permissions as Unix octal strings. `FILETYPE` maps a Hadoop `FileStatus` to `FILE`, `DIRECTORY`, or `SYMLINK`. `Operation` enumerates supported WebHDFS-style operations and binds each to an HTTP method.

## Control Flow
Consumers switch on `Operation` values after `HttpFSParametersProvider` parses the `op` query parameter. `FILETYPE.getType()` checks file, directory, then symlink and throws for unknown statuses.

## State and Persistence Behavior
The interface is static constants only.

## Dependencies and Integration Points
Constants are used by request parsing, routing, filters, JSON serialization in `FSOperations`, and response generation in `HttpFSServer`. The operation list must stay aligned with `HttpFSParametersProvider.PARAMS_DEF` and `HttpFSServer` switch coverage.

## Risks and Edge Cases
Several operations are declared even when `HttpFSServer` currently rejects them as unsupported. This is useful for compatibility but can surprise callers expecting full WebHDFS support. `DEFAULT_PERMISSION` is octal `0755`; permission string conversion omits zero padding.

## Test Signals
No direct tests in this subset. Operation compatibility is exercised through server/API integration tests.
