# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ExceptionProvider.java

## Purpose
`ExceptionProvider` is the default JAX-RS exception mapper for HttpFS support classes.

## Important APIs, types, and functions
It implements `ExceptionMapper<Throwable>`. `toResponse()` maps all throwables to HTTP `BAD_REQUEST` using `HttpExceptionUtils.createJerseyExceptionResponse`. Protected helpers create responses, extract first-line messages, and log at debug level.

## Control flow
Subclasses can override status selection or logging. The base class always returns a Jersey exception response with status 400.

## State and persistence behavior
No mutable state is stored.

## Dependencies and integration points
Jersey discovers providers from `org.apache.ozone.lib.wsrs` as configured in web.xml. HttpFS-specific exception providers may extend or coexist with this mapper.

## Risks and edge cases
Mapping every throwable to bad request can hide server-side failures unless overridden. Debug-only logging may make production diagnostics depend on response bodies.

## Test signals
REST error response tests would exercise this mapper; none are in this subset.
