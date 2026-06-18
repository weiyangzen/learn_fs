# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBTenantState.java

Purpose: Immutable persisted state for an Ozone tenant and its backing volume/roles/policies.

Important APIs/types/functions: `CODEC` delegates to `TenantState` protobuf. Fields include tenant ID, bucket namespace name, user role, admin role, bucket namespace policy, and bucket policy. Implements `Comparable` by tenant ID. `getProtobuf` and `getFromProtobuf` round trip all fields.

Control flow and state: Immutable value object. Equality/hash include all fields; ordering includes only tenant ID.

State and persistence behavior: Persisted in OM tenant state table using protobuf codec. Empty bucket namespace name is documented as possible but should not normally happen.

Dependencies and integration points: Used by tenant creation/deletion, Ranger/ACL policy coordination, and tenant listing.

Risks: `compareTo` can report equality for distinct objects with the same tenant ID but different policy fields, which is suitable for tenant-keyed sorted sets but not total object ordering. Null tenant ID would break comparison.

Test signals: Codec round trips, equality/hash behavior, compare ordering, and tenant delete/list flows.
