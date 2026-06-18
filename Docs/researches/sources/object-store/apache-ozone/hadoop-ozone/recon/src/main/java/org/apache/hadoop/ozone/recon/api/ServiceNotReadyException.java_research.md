<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ServiceNotReadyException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ServiceNotReadyException.java

## Purpose

`ServiceNotReadyException` is a lightweight runtime exception used by Recon APIs to signal that an internal service or metadata source is not initialized enough to satisfy a request.

## Important APIs and Types

It extends `RuntimeException` and provides a single message constructor.

## Control Flow

The class has no internal branching. Callers such as `OMDBInsightEndpoint.getListKeysResponse` can catch it specially and convert it to a service-unavailable response with an initializing body.

## State and Persistence

It carries only the exception message and has no persistence.

## Dependencies and Integration Points

It integrates with endpoint error handling where checked exceptions would be awkward through helper paths.

## Risks and Edge Cases

As an unchecked exception, it must be caught at appropriate API boundaries or it will become a generic 500. Its semantics rely on consistent use by lower-level helpers.

## Test Signals

Tests should assert API translation to HTTP 503 where the exception is intentionally caught, and generic error behavior where it is not.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ServiceNotReadyException.java -->
