# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Groups.java

## Purpose
`Groups` defines the service interface for resolving a user to Hadoop group names.

## Important APIs, types, and functions
It exposes `getGroups(String user)` returning `List<String>` and throwing `IOException`.

## Control flow
No behavior is defined beyond delegation.

## State and persistence behavior
The interface owns no state.

## Dependencies and integration points
`GroupsService` implements it with Hadoop `org.apache.hadoop.security.Groups`. Authentication and proxyuser checks can depend on group resolution.

## Risks and edge cases
Group resolution is environment-sensitive and can block or fail depending on configured mapping providers.

## Test signals
No direct tests in this subset; integration is through HttpFS authentication and proxy user flows.
