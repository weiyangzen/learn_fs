# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ObjectPathResolver.java

Purpose: `ObjectPathResolver` is a small interface for resolving object IDs to filesystem paths in snapshot-related code.

Important APIs and types: `getAbsolutePathForObjectIDs(Optional<Set<Long>> objIds, boolean skipUnresolvedObjs)` is the core contract and may throw `IOException`. The default overload calls it with `skipUnresolvedObjs=false`.

Control flow and state: the interface itself has no state or implementation beyond the default overload. Implementations decide how to traverse metadata and how to handle missing IDs.

Dependencies and integration points: it is implemented by `FSODirectoryPathResolver`, which resolves FSO directory IDs through OM directory tables. Other snapshot diff or filtering code can depend on the interface rather than specific table layouts.

Risks: callers must understand the behavior of `Optional.empty()` and the unresolved-object flag in the concrete implementation they use. The default overload is strict and can throw for unresolved object IDs.

Test signals: tests target implementations, especially `TestFSODirectoryPathResolver`.
