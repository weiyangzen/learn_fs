# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/aclDrawer/aclDrawer.tsx


Purpose: Legacy ACL drawer component showing ACL entries for an OM entity in an AntD drawer/table.

Important APIs/types/functions: Exports `AclPanel` class. Props include `visible`, `acls`, `objName`, and `objType`. Uses `renderAclList`, `renderAclIdentityType`, `IAcl`, `ACLIdentityTypeList`, and color maps.

Control flow/state/persistence: Copies incoming `visible` prop into local state in `componentWillReceiveProps`; closing only sets local state false. Table columns sort/filter by name/type and render ACL rights as tags.

Dependencies/integration points: Used by legacy volume/bucket/object metadata views; depends on AntD `Drawer`, `Table`, `Tag`, and OM ACL types/constants.

Risks/test signals: `componentWillReceiveProps` is deprecated, and the file references `RouteComponentProps` without importing it. Parent may not learn about drawer close because no `onClose` callback is exposed.
