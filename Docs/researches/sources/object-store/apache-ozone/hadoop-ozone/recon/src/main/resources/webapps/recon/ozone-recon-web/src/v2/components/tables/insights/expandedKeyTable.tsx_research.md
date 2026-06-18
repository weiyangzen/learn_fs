# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedKeyTable.tsx

Purpose: Nested table for mismatch key details under an expanded container row.

Important APIs, types, and functions: Exports `ExpandedKeyTable`. Props are `loading`, mismatch key `data`, and shared `paginationConfig`.

Control flow: Formats volume, bucket, key, IEC size, creation time, and modification time into a plain AntD table.

State and persistence behavior: Stateless render component with no persistence.

Dependencies: Uses AntD table, `moment`, `filesize`, and `MismatchKeys` type.

Integration points: Used as expanded-row content by container mismatch/deleted-container insights.

Risks and edge cases: Row key `uid` must be supplied by the API; if absent, React row identity degrades. `moment(date)` assumes parseable API strings.

Test signals: Cover loading state, missing/duplicate UID, invalid dates, zero data size, and pagination handoff.
