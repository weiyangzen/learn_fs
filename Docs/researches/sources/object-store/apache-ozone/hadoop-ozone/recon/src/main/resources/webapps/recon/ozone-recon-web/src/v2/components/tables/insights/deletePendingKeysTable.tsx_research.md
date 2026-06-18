# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingKeysTable.tsx

Purpose: Aggregates OM delete-pending key entries by key name and provides expandable details for individual pending-key versions.

Important APIs, types, and functions: Exports `DeletePendingKeysTable`. Defines aggregate row and expanded-list helper types internally.

Control flow: Fetches `/api/v1/keys/deletePending?limit=...`, reduces each `omKeyInfoList` to total data size and count, stores original lists separately, filters aggregate rows by path, and renders `ExpandedPendingKeysTable` for matching rows.

State and persistence behavior: Local aggregate `data`, `searchTerm`, and `expandedDeletePendingKeys`. API state is managed by `useApiData`.

Dependencies: Uses AntD table, `Search`, `SingleSelect`, `ExpandedPendingKeysTable`, `byteToSize`, `useDebounce`, and insights types.

Integration points: Used by Insights pending deletion tabs.

Risks and edge cases: The reducer assumes `omKeyInfoList[0]` exists and will fail on empty lists. Expansion matches only `keyName`, so duplicate key names can merge details. Row key is also `keyName`.

Test signals: Cover empty `omKeyInfoList`, duplicate keys in different buckets, aggregate size/count correctness, limit refetch, and expansion detail filtering.
