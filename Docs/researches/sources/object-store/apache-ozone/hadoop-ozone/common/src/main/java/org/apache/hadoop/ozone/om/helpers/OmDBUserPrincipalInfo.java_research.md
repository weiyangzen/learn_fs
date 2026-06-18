# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBUserPrincipalInfo.java

Purpose: Persisted mapping from a user principal to the tenant access IDs associated with that principal.

Important APIs/types/functions: `CODEC` delegates to `TenantUserPrincipalInfo`. Constructor copies the input set. `addAccessId`, `removeAccessId`, and `hasAccessId` mutate/query the set. `getProtobuf` writes all access IDs; `getFromProtobuf` rebuilds from the list.

Control flow and state: Mutable set holder. `getAccessIds` returns the internal set directly.

State and persistence behavior: Stored in OM tenant user principal table. Mutations must be followed by table updates by caller code.

Dependencies and integration points: Used by tenant user/access-ID management to answer which access IDs belong to a Kerberos principal.

Risks: Internal set exposure allows external mutation outside OM table update discipline. Builder with null access IDs causes construction failure.

Test signals: Codec round trip, add/remove idempotency, duplicate access IDs, and persistence after mutation in tenant manager tests.
