# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONProvider.java

## Purpose
`JSONProvider` is a Jersey message-body writer for objects implementing JSON.simple `JSONStreamAware`.

## Important APIs, types, and functions
The provider produces UTF-8 JSON. `isWriteable()` accepts `JSONStreamAware`, `getSize()` returns `-1`, and `writeTo()` invokes `writeJSONString`, writes a line separator, and flushes.

## Control flow
Serialization delegates to the object, allowing timers, variables, and samplers to stream their own JSON.

## State and persistence behavior
No mutable state is stored.

## Dependencies and integration points
It integrates with `InstrumentationService.Timer`, `VariableHolder`, and `Sampler`, which implement `JSONStreamAware`.

## Risks and edge cases
Any exception in the object's JSON writer propagates as an IO/JAX-RS failure. Objects control their own JSON shape.

## Test signals
REST or instrumentation endpoint tests would validate behavior; none are included here.
