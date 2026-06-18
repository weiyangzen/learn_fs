# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SkipTracing.java

## Purpose
Runtime method annotation marking methods that should not be traced by proxy-based tracing.

## Important APIs and types
The annotation targets methods and is retained at runtime.

## Control flow and state
No runtime behavior by itself. `TraceAllMethod` inspects it on delegate methods.

## Dependencies and integration points
Used with `TracingUtil.createProxy` and `TraceAllMethod`.

## Risks and test signals
Tests should ensure annotations on implementation methods are honored by the proxy. Interface-method annotations alone may not be enough because `TraceAllMethod` scans delegate class methods.
