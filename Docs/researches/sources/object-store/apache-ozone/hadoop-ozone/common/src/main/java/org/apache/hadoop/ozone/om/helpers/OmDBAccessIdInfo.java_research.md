# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDBAccessIdInfo.java

Purpose: Immutable persisted metadata for one tenant access ID, including tenant ID, user principal, admin flag, and delegated-admin flag.

Important APIs/types/functions: `CODEC` delegates to `ExtendedUserAccessIdInfo` protobuf. Constructor and builder set fields. `getProtobuf` and `getFromProtobuf` convert to/from DB representation.

Control flow and state: Immutable after construction. Delegated-admin is documented as effective only when admin is true but not enforced in the class.

State and persistence behavior: Persisted in OM tenant access-ID tables through the delegated protobuf codec.

Dependencies and integration points: Used by tenant/user access management and authorization checks.

Risks: No validation prevents delegated admin without admin, null tenant ID, or null principal. Codec copy type is shallow, acceptable because fields are immutable strings/booleans.

Test signals: Codec round trip, admin/delegated combinations, and tenant access authorization flows consuming persisted values.
