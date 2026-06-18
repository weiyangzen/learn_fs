# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/exceptions/SCMException.java

## Purpose
General SCM `IOException` carrying an SCM-specific `ResultCodes` enum for client and RPC error decoding.

## Important APIs, Types, And Functions
Constructors support message-only remote unwrap, result-only, message/result, message/cause/result, and cause/result. `getResult()` returns the code. `ResultCodes` enumerates allocation, pipeline, container, safe mode, leadership, CA rotation, timeout, and unsupported-operation failures.

## Control Flow
SCM services throw this or subclasses; Hadoop RPC can unwrap via required constructors; clients inspect result codes to decide retry or user-facing errors.

## State And Persistence
State is transient exception data. Enum ordinals are compatibility-sensitive, as comments warn not to delete removed revocation codes.

## Dependencies And Integration Points
Integrated by container, pipeline, SCM HA, security, and admin services. Subclasses in this group map specific errors to result codes.

## Risks And Test Signals
Null result from message-only constructor must be handled. Enum ordinal stability is an upgrade risk. Tests should cover remote exception unwrapping, retry classification, and result mapping for subclasses.
