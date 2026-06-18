# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IAccessAuthorizer.java

Purpose: Public extension interface for Ozone ACL authorization providers, including native and external systems such as Ranger.

Important APIs and types: Core method `checkAccess(IOzoneObj, RequestContext)` returns authorization decision or throws `OMException`. Default `generateAssumeRoleSessionPolicy` rejects STS support with `NOT_SUPPORTED_OPERATION`. Default `isNative` returns false. Nested enums `ACLType` and `ACLIdentityType` define permissions and identity classes.

Control flow: `ACLType` maps compact string rights from `OzoneConsts` to enum values and back, renders `BitSet` ACLs, parses comma-separated enum names, and enforces a maximum of 16 ACLs because other encoding code assumes that width. `ACLIdentityType` maps user/group/world/anonymous/client-IP identity categories to string constants.

State and persistence behavior: Interface is stateless, but enum names, ordinals, and string encodings are persisted in ACL metadata and external policies. `ASSUME_ROLE` extends the permission model for STS token creation.

Dependencies and integration points: Used by OM ACL checks, Ranger plugin integration, native authorizer, request contexts, Ozone ACL protobuf/model conversion, and tenant/S3 STS workflows.

Risks: `getAclTypeFromOrdinal` condition appears intended to reject ordinal `< 0` or `>= length`, but the `&&` expression only rejects values greater than length and positive; negative ordinals can still reach array indexing. Adding ACL values beyond 16 triggers assertion and requires encoding changes. String parsing with `Enum.valueOf` in `parseList` expects enum names, not short ACL letters.

Test signals: Exhaustive string-to-enum and enum-to-string mapping, BitSet rendering, invalid/negative ordinal behavior, parse-list whitespace handling, default STS rejection, and provider-specific `checkAccess` contracts.
