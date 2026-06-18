# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/bucketsTable.tsx

Purpose: Displays bucket inventory rows with sorting, storage/layout filters, quota bars, and a dynamic ACL action column.

Important APIs, types, and functions: Exports `BucketsTable` and mutable `COLUMNS`. Helpers render versioning icons, storage-type icons, and layout tags.

Control flow: On mount the table appends or replaces an ACL column that captures the current `handleAclClick`. It filters visible columns from parent-selected options and filters rows by the selected search column before rendering AntD `Table`.

State and persistence behavior: No own state, but it mutates module-level `COLUMNS` and the `selectedColumns` prop array in its mount effect.

Dependencies: Uses AntD table/tag/icons, `moment`, `QuotaBar`, `nullAwareLocaleCompare`, and bucket type constants.

Integration points: Consumed by `pages/buckets/buckets.tsx`; ACL links open `AclPanel` in the parent.

Risks and edge cases: Mutating exported `COLUMNS` and props can duplicate/stale action columns across mounts or tests. `bucket[searchColumn].includes` assumes all searchable fields are strings. ACL effect has an empty dependency list despite using props.

Test signals: Cover ACL callback after remount, selected-column filtering with fixed columns, storage/layout filters, search by name and volume, null owner sorting, and quota rendering.
