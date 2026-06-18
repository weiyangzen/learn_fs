# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/volume.types.ts

Purpose: Defines v2 volume API rows, response, page state, and table props.

Important APIs/types/functions: Exports `Volume`, `VolumesResponse`, `VolumesState`, and `VolumesTableProps`. It imports common `Acl` and multi-select `Option`.

Control flow: Type-only module. The table props define ACL click callbacks, selected columns, and search by `volume`, `owner`, or `admin`.

State and persistence: No runtime state. `VolumesState` models local data, last refresh, and column options.

Dependencies and integration points: Used by v2 Volumes page/table and ACL drawer integration. Mirrors `/api/v1/volumes` response fields.

Risks: `acls` is optional, so drawer/table code must handle absent ACLs. Quota fields are numeric and likely bytes/counts but not branded by units. Backend additions are ignored unless the type and mapper are updated.

Test signals: Tests should cover ACL-present and ACL-missing rows, quota edge values, search over volume/owner/admin, and empty response handling.
