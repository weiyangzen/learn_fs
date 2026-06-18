# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/volumesTable.tsx

Purpose: Displays volume inventory with quotas, namespace capacity, navigation to buckets, and a dynamic ACL action column.

Important APIs, types, and functions: Exports `VolumesTable` and mutable `COLUMNS`; props come from `VolumesTableProps`.

Control flow: On mount appends/replaces an Actions column that links to `/Buckets?volume=...` and calls parent ACL handler. It filters selected columns and rows by the requested search column.

State and persistence behavior: No local state, but mutates module-level `COLUMNS` and the `selectedColumns` prop array.

Dependencies: Uses AntD table, `QuotaBar`, `byteToSize`, `moment`, and `Link` from react-router.

Integration points: Consumed by the Volumes page; the generated bucket link seeds the Buckets page volume filter.

Risks and edge cases: Mutable columns/prop mutation can leak across mounts. Search assumes selected field supports `includes`. Action-column effect does not update when `handleAclClick` changes.

Test signals: Cover action links, ACL callback after remount, quota NA behavior for -1, selected columns, search by owner/admin/volume, and duplicate mount behavior.
