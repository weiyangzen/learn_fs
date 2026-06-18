# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/package-info.java

## Purpose
This descriptor documents the internal service-definition package for HttpFS.

## Important APIs, types, and functions
The package defines `FileSystemAccess`, `Groups`, `Instrumentation`, `Scheduler`, and `FileSystemAccessException`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
These interfaces are the contracts implemented by `org.apache.ozone.lib.service.*` concrete services and retrieved through `Server#get`.

## Risks and edge cases
Interface changes in this package have broad impact on service wiring.

## Test signals
Compilation and service-integration tests are the relevant signals.
