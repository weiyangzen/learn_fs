# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/package-info.java

## Purpose
This descriptor documents the JAX-RS support package.

## Important APIs, types, and functions
The package provides typed query parameters, request parameter containers/providers, JSON message writers, streaming entities, and exception mapping.

## Control flow
No executable behavior is present in the descriptor.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
Both web descriptors register this package with Jersey provider scanning alongside HttpFS server resources.

## Risks and edge cases
Changes here affect REST request parsing and response serialization across the gateway.

## Test signals
REST integration tests and Jersey provider discovery validate this package.
