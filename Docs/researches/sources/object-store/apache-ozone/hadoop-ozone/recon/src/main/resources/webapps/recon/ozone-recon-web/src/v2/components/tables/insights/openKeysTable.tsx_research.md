# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/openKeysTable.tsx

Purpose: Displays open keys, switching between FSO and Non-FSO result sets, with limit selection and debounced path search.

Important APIs, types, and functions: Exports `OpenKeysTable`. Props include selected limit, pagination config, and limit-change handler.

Control flow: Builds `/api/v1/keys/open?includeFso=...&includeNonFso=...&limit=...`, maps the active result array to rows with a `type`, filters by `path`, and renders replication type/factor/EC details.

State and persistence behavior: Local `isFso` and `searchTerm`; API state is from `useApiData`, which refetches when the URL changes.

Dependencies: Uses AntD dropdown/menu/table, `Search`, `SingleSelect`, `useDebounce`, `useApiData`, byte/time formatting helpers, and insights types.

Integration points: Insights open-key tab.

Risks and edge cases: Only one of FSO or Non-FSO is fetched at a time; switching type discards the other view. Row key is `key`, which may not be globally unique. Search is path-only.

Test signals: Cover FSO/Non-FSO toggle URLs, RATIS versus EC replication rendering, limit changes, duplicate keys, and long path search.
