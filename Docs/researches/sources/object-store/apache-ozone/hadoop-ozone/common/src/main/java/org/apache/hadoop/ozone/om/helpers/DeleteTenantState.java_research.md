# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/DeleteTenantState.java

Purpose: Wrapper for tenant deletion response state, reporting the associated volume and remaining volume reference count.

Important APIs/types/functions: Constructor and builder set `volumeName` and `volRefCount`. `getProtobuf` emits `DeleteTenantResponse`; `fromProtobuf` reconstructs the object.

Control flow and state: Immutable after construction. Builder has no validation.

State and persistence behavior: Response/transport DTO only. It mirrors protobuf fields and is not itself a DB codec.

Dependencies and integration points: Used by tenant delete APIs that need to tell clients whether the tenant volume can be cleaned up or still has references.

Risks: Allows null volume names and negative counts unless upstream validation prevents them.

Test signals: Protobuf round trip and builder field propagation, especially zero and nonzero reference counts.
