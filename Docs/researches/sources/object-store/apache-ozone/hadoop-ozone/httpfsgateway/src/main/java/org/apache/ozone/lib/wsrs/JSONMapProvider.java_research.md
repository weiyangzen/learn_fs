# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONMapProvider.java

## Purpose
`JSONMapProvider` is a Jersey message-body writer for serializing Java `Map` responses as UTF-8 JSON.

## Important APIs, types, and functions
It is annotated with `@Provider` and produces `application/json; charset=utf-8`. `isWriteable()` accepts `Map` subclasses, `getSize()` returns `-1`, and `writeTo()` writes with JSON.simple `JSONObject.writeJSONString`, appends a line separator, and flushes.

## Control flow
Serialization is one-pass to the response output stream through an UTF-8 writer.

## State and persistence behavior
No mutable state exists beyond the static line separator.

## Dependencies and integration points
Jersey loads it from the `org.apache.ozone.lib.wsrs` provider package in both web descriptors. It can serialize instrumentation snapshots and REST response maps.

## Risks and edge cases
Map contents must be JSON.simple-compatible. It does not set response headers beyond provider annotations.

## Test signals
REST response tests would validate JSON output; none are in this subset.
