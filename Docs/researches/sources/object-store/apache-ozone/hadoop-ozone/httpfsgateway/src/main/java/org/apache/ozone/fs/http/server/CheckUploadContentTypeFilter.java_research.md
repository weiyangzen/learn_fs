# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/CheckUploadContentTypeFilter.java

## Purpose
`CheckUploadContentTypeFilter` enforces that data-bearing HttpFS upload requests use `application/octet-stream`.

## Important APIs, Types, and Functions
The servlet `Filter` maintains a static `UPLOAD_OPERATIONS` set containing `APPEND` and `CREATE`. `doFilter()` checks PUT/POST requests with matching `op` and `data=true`. If the request content type matches `HttpFSConstants.UPLOAD_CONTENT_TYPE`, it continues the chain; otherwise it returns HTTP 400 with a JSON error body serialized by `JsonUtil`.

## Control Flow
The filter only validates actual upload legs of two-step create/append flows. Redirect negotiation requests without `data=true` are not constrained. Bad requests are handled in the filter without entering JAX-RS routing.

## State and Persistence Behavior
No persistent state. Static upload operation set is initialized once.

## Dependencies and Integration Points
It depends on servlet APIs, `HttpFSConstants`, `HttpFSParametersProvider.DataParam`, Hadoop `StringUtils`, and `JsonUtil`. It should be wired in the HttpFS web application filter chain.

## Risks and Edge Cases
The equality check is strict against the full content type string ignoring case; values with charset parameters may be rejected even if semantically octet-stream. Only create and append are treated as upload operations.

## Test Signals
No direct test in this subset. Coverage should exercise accepted content type, missing/incorrect content type, and redirect negotiation paths.
