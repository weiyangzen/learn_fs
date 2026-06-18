# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/GroupsService.java

## Purpose
`GroupsService` implements the HttpFS `Groups` interface using Hadoop's group-mapping subsystem.

## Important APIs, types, and functions
`init()` copies service-scoped configuration into a Hadoop `Configuration` and constructs `org.apache.hadoop.security.Groups`. `getInterface()` returns `Groups.class`. `getGroups(user)` delegates to Hadoop.

## Control flow
Initialization occurs during server boot. Requests later call `getGroups`, which may use Hadoop's configured cache and mapping provider.

## State and persistence behavior
State is one Hadoop `Groups` instance and its internal caches. No explicit persistence occurs.

## Dependencies and integration points
It extends `BaseService`, uses `ConfigurationUtils.copy`, and integrates with authentication/proxyuser paths that need group membership.

## Risks and edge cases
Behavior depends on Hadoop group mapping configuration and host environment. IO failures propagate to callers.

## Test signals
No direct tests in this subset; authentication integration tests would expose mapping failures.
