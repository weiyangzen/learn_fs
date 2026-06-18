# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccessException.java

## Purpose
`FileSystemAccessException` reports validation, authentication, configuration, and execution failures from filesystem access.

## Important APIs, types, and functions
The nested `ERROR` enum covers missing service properties, Kerberos failure, executor errors, invalid non-service-created configurations, namenode validation, missing `fs.defaultFS`, health failures, wrapped generic messages, invalid auth mode, missing Hadoop config directory, and config load failures.

## Control flow
The class delegates all formatting and cause handling to `XException`.

## State and persistence behavior
Only exception metadata is stored.

## Dependencies and integration points
`FileSystemAccessService` throws these codes both directly and wrapped in `ServiceException` during service initialization.

## Risks and edge cases
Several error paths wrap broad exceptions, so callers may need to inspect causes for detailed Hadoop failures.

## Test signals
Tests that pass invalid versions/configurations or missing filesystem properties would assert these codes; this subset's metrics test avoids the failure paths.
