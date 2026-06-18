# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/DatanodeAdminError.java

## Purpose
Small DTO for returning datanode administration failures as a hostname plus error message.

## Important APIs, Types, And Functions
`DatanodeAdminError(String host, String error)` stores two strings. `getHostname()` and `getError()` expose them.

## Control Flow
No logic exists beyond construction and access.

## State And Persistence
Instances are mutable internally but have no setters. They are transient result objects for admin commands or APIs.

## Dependencies And Integration Points
Used by SCM datanode admin/decommission/maintenance command surfaces to report per-node failures.

## Risks And Test Signals
Risk is minimal; lack of null validation means callers may emit incomplete API responses. Tests should verify command/API serialization of failures.
