# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/columnSearch.tsx


Purpose: Legacy AntD table column-search prop builder.

Important APIs/types/functions: `ColumnSearch` `PureComponent`, `getColumnSearchProps(dataIndex)`, `handleSearch`, and `handleReset`.

Control flow/state/persistence: Renders filter dropdown with input/search/reset buttons, tracks input ref, focuses/selects on dropdown open, and filters records by scalar string or array/object values.

Dependencies/integration points: Spread into AntD table column definitions in legacy tables.

Risks/test signals: `if (record[dataIndex] !== undefined || record[dataIndex] !== null)` should be `&&`; as written it attempts `toString()` on null/undefined. Object detection via `typeof {}` is imprecise.
