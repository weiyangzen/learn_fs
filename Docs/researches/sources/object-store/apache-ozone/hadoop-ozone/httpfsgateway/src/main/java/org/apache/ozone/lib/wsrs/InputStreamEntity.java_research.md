# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/InputStreamEntity.java

## Purpose
`InputStreamEntity` streams an input stream to a JAX-RS response while honoring offset/length and updating HttpFS bytes-read metrics.

## Important APIs, types, and functions
The constructor stores `InputStream`, offset, and length. `write(OutputStream)` skips the offset with `IOUtils.skipFully`, copies all remaining bytes when `len == -1` or exactly `len` bytes otherwise via `FSOperations.copyBytes`, then increments `HttpFSServerMetrics` bytes-read when metrics are available.

## Control flow
The stream copy is synchronous inside Jersey's `StreamingOutput` callback. Metrics are updated after copy completion.

## State and persistence behavior
State is the stream and range parameters. It does not close the input stream directly in this file; stream lifecycle is owned by callers/filters.

## Dependencies and integration points
It integrates Hadoop IO utilities, HttpFS copy buffer logic, `HttpFSServerWebApp`, and metrics. It is used for read/open-style responses.

## Risks and edge cases
Invalid offsets can fail during skip. If copy fails, metrics are not incremented. The filesystem backing the stream must remain open until streaming completes, which is why release filters are important.

## Test signals
Read metrics tests would validate `incrBytesRead`; this subset's metrics test covers write metrics through create/append.
