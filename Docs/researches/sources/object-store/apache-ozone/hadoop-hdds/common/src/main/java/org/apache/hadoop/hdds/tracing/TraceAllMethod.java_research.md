# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TraceAllMethod.java

## Purpose
Java dynamic-proxy invocation handler that traces calls to all delegate methods except methods annotated with `SkipTracing`.

## Important APIs and types
The constructor scans public delegate methods, skips `Object` methods, records parameter-type signatures, and marks methods with `SkipTracing`. `invoke` finds the matching delegate method, optionally creates a span named `<interfaceName>.<methodName>`, invokes the delegate, and unwraps reflection causes.

## Control flow and state
The handler caches a nested map from method name to parameter types to `(shouldSkip, Method)`. Skipped methods invoke directly. Non-skipped methods run inside `TracingUtil.createActivatedSpan`, which ends the span on close. A missing method produces `NoSuchMethodException`.

## Dependencies and integration points
Created by `TracingUtil.createProxy` when tracing is enabled. It depends on reflection, Apache Commons `Pair`, and `SkipTracing`.

## Risks and test signals
Tests should cover overloaded methods, exception unwrapping, skip annotation behavior, missing method failure, and Object method behavior. Parameter-type arrays are used as map keys but searched by array equality, so direct map lookup is intentionally avoided.
