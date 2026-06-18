# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServiceException.java

## Purpose
`ServiceException` is the checked exception type for failures inside `Service` implementations.

## Important APIs, types, and functions
It extends `ServerException` and accepts any `XException.ERROR` plus formatting parameters.

## Control flow
No additional logic is added over the parent exception construction.

## State and persistence behavior
Only inherited exception state is stored.

## Dependencies and integration points
`BaseService` subclasses throw this type during initialization and post-initialization. `FileSystemAccessService` wraps Hadoop configuration and Kerberos failures with this exception.

## Risks and edge cases
Because it accepts any `XException.ERROR`, service-specific domains can share one exception type but logs must inspect the error code for source context.

## Test signals
Indirect tests are service initialization failures and server boot behavior.
