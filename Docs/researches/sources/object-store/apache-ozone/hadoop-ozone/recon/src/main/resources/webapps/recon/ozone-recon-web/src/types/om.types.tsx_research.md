# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/om.types.tsx


Purpose: Legacy Ozone Manager metadata types for ACLs, volumes, and buckets.

Important APIs/types/functions: Exports `IAcl`, `IVolume`, `IBucket`, bucket storage/layout lists and union types, `ACLIdentityTypeList`, `ACLIdentity`, `ACLRightList`, and `ACLRight`.

Control flow/state/persistence: Type-only module plus enum-like arrays.

Dependencies/integration points: Used by legacy ACL drawer, volume/bucket views, quota display, and metadata tables.

Risks/test signals: The list-to-union pattern uses mutable arrays, so types are broader than literal unions unless `as const` is used. Backend enum drift requires updates.
