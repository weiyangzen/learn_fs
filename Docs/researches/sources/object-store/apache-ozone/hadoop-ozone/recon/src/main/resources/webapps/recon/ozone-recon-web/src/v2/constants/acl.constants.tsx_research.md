# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/acl.constants.tsx

Purpose: Defines Ant Design color mappings for ACL identity types and rights.

Important APIs, types, and functions: Exports `AclIdColorMap` and `AclRightsColorMap` objects.

Control flow: No control flow; consumers look up a color by ACL enum-like string.

State and persistence behavior: Static constants only.

Dependencies: No imports.

Integration points: Used by ACL drawer/panel rendering to color identity and right tags.

Risks and edge cases: Maps are untyped, so new backend ACL strings silently produce undefined/default colors. Color names assume AntD tag palette support.

Test signals: Validate all known ACL identity/right enums are present and unknown values fall back safely in consumers.
