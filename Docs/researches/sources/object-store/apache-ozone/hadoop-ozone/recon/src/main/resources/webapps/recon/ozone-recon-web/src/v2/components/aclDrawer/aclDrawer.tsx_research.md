# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/aclDrawer/aclDrawer.tsx


Purpose: V2 functional ACL drawer for displaying ACLs on volumes/buckets/objects.

Important APIs/types/functions: Default export `AclPanel`, `AclDrawerProps`, `renderAclList`, `renderAclIdentityType`, `COLUMNS`, V2 ACL types/constants.

Control flow/state/persistence: Mirrors `visible` prop into `isVisible` with `useEffect`; uses parent `onClose` for drawer close. Renders AntD Table with typed columns, filtering ACL type and sorting name/type.

Dependencies/integration points: Used by V2 namespace/OM metadata views. Depends on V2 ACL constants and AntD Drawer/Table.

Risks/test signals: Local `isVisible` duplicates controlled prop and can desync briefly. ACL color maps require updates for new ACL enum values.
