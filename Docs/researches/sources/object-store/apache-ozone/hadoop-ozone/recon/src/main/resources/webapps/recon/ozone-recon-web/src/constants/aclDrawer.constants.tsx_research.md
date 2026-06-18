# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/aclDrawer.constants.tsx


Purpose: Legacy color maps for ACL identity types and ACL rights.

Important APIs/types/functions: Exports `aclIdentityTypeColorMap` and `aclRightColorMap` with string index signatures.

Control flow/state/persistence: None; constants only.

Dependencies/integration points: Used by legacy `AclPanel` to color AntD `Tag` elements for identities and rights.

Risks/test signals: Maps are not type-checked against `ACLIdentityTypeList`/`ACLRightList`; new backend ACL enum values render uncolored unless the map is updated.
