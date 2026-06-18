# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/HostnameFilter.java

## Purpose
`HostnameFilter` resolves the remote client address to a canonical hostname and exposes it to downstream request processing through a thread-local.

## Important APIs, types, and functions
`doFilter()` reads `ServletRequest#getRemoteAddr`, resolves with `InetAddress.getByName(...).getCanonicalHostName()`, stores the result in `HOSTNAME_TL`, invokes the chain, and clears the thread-local. `get()` returns the current hostname.

## Control flow
Null or unresolvable remote addresses are logged and represented as `"???"`. Cleanup always runs in finally.

## State and persistence behavior
Only per-thread request context is stored. No persistence occurs.

## Dependencies and integration points
`MDCFilter` reads this thread-local to put `hostname` into SLF4J MDC. Both web descriptors map this filter to all requests.

## Risks and edge cases
Reverse DNS can add latency. The filter order in both web descriptors maps `MDCFilter` before `hostnameFilter`, so MDC will not see a hostname unless the container applies an ordering different from declaration order or mapping order is changed.

## Test signals
No direct tests in this subset. Request logging output would expose missing hostname MDC.
