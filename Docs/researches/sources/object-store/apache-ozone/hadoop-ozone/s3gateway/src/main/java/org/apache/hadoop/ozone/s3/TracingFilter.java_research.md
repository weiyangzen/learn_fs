# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/TracingFilter.java

Purpose: `TracingFilter` creates and closes OpenTelemetry/HDDS tracing spans around JAX-RS resource execution, with special handling for streaming object downloads.

Important APIs and flow: the request filter ends any active span, names a new span from resource class and method, creates it from W3C HTTP headers, and stores the closeable in the request context. The response filter closes the span immediately except for `GET ObjectEndpoint.get`, where it wraps the entity output stream and closes the span only after streaming output is closed.

State, dependencies, risks, and tests: state is the request property holding `TraceCloseable`. It depends on `ResourceInfo`, `TracingUtil`, `OzoneConfigurationHolder`, and `WrappedOutputStream`. Risks include ending an unrelated active span, missing closure on streaming write failures before stream close, and class/method-name based detection breaking after refactors. Tests should cover normal endpoint span closure, streaming GET delayed closure, and null entity stream fallback.
