# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/acl.types.ts

Purpose: Defines v2 ACL identity/right constants and the common ACL row shape used by volume and bucket UI.

Important APIs/types/functions: Exports `ACLIdentityTypeList`, union type `ACLIdentity`, `ACLRightList`, union type `ACLRight`, and `Acl` with `type`, `name`, `scope`, and `aclList`.

Control flow: Type-only and constant module; no runtime logic except exporting arrays used for validation or UI option generation.

State and persistence: No state. Constants are immutable by TypeScript `as const` typing but not frozen at runtime.

Dependencies and integration points: Referenced by v2 bucket/volume types and ACL drawer components. Values correspond to Ozone ACL identity and right enums.

Risks: `Acl.type` remains plain `string` rather than `ACLIdentity`, and `aclList` is `string[]` rather than `ACLRight[]`, so compile-time validation is weaker than the exported lists imply. Backend enum changes require updating these lists.

Test signals: Type-level or component tests should ensure ACL drawer/selectors render every identity/right and tolerate unknown backend values when types remain strings.
