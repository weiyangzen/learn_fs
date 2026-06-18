# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/MDCFilter.java

## Purpose
`MDCFilter` enriches request logs by populating SLF4J MDC with request context.

## Important APIs, types, and functions
`doFilter()` clears MDC, reads `HostnameFilter.get()`, principal name, HTTP method, and path info, puts available values under `hostname`, `user`, `method`, and `path`, delegates to the chain, and clears MDC in finally.

## Control flow
The filter assumes the request is an `HttpServletRequest`. Null principal and path are tolerated.

## State and persistence behavior
State is MDC thread-local context for the current request only.

## Dependencies and integration points
It integrates servlet filters with SLF4J/reload4j log patterns. Web descriptors map it to all requests.

## Risks and edge cases
If it runs before `HostnameFilter`, hostname will be absent. Non-HTTP servlet requests would cause a class cast failure. Clearing MDC can remove context set by upstream filters.

## Test signals
No direct tests in this subset; log formatting and request traces are runtime signals.
