# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/package-info.java

## Purpose
This descriptor documents the Hadoop service provider package.

## Important APIs, types, and functions
The package contains `FileSystemAccessService`, the concrete Hadoop-backed implementation of `FileSystemAccess`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package bridges HttpFS service APIs to Hadoop security and filesystem clients.

## Risks and edge cases
Documentation should remain aligned if additional Hadoop-backed services are added.

## Test signals
Compilation and service integration tests are the relevant signals.
