# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/StorageContainerException.java

## Purpose
Base `IOException` subtype for storage-container protocol failures with a datanode `ContainerProtos.Result` code.

## Important APIs, Types, And Functions
Constructors cover result-only, message/result, message/cause/result, and cause/result. `getResult()` exposes the protocol result.

## Control Flow
Datanode handlers throw this or subclasses; RPC layers translate result codes into container command responses.

## State And Persistence
Only exception message/cause and final result code are stored. No persistence.

## Dependencies And Integration Points
Depends on datanode `ContainerProtos.Result`. Integrated by container command handlers, clients, and tests that assert wire errors.

## Risks And Test Signals
The result-only constructor leaves message null. Tests should cover every constructor, result-code preservation, and client-side translation.
