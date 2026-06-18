# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/pipelines/pipelines.tsx

## Purpose
This React class component renders the Recon Pipelines page. It fetches pipeline metadata from `/api/v1/pipelines` and displays active pipeline rows in an Ant Design table with search, sort, status filtering, replication icons, leader metrics, and auto-refresh.

## Important APIs, types, and functions
`PipelineStatusList` defines allowed pipeline status filter values. `IPipelineResponse` models each table row, including `pipelineId`, `status`, replication type/factor, leader node, datanodes, leader election metrics, lifetime, and container count. `COLUMNS` defines Ant table columns and renderers. `_loadData` uses `AxiosGetHelper` to fetch `IPipelinesResponse`. `onShowSizeChange` and `onTabChange` are placeholders for pagination logging and future inactive-pipeline support.

## Control flow, state, and persistence
The component stores `activeLoading`, `activeDataSource`, `activeTotalCount`, and `lastUpdated` in memory. On mount it fetches data and starts `AutoReloadHelper` polling. On unmount it stops polling and cancels the module-level `cancelPipelineSignal`. Render wraps searchable columns using `ColumnSearch` at render time and uses `rowKey='pipelineId'`.

## Dependencies and integration points
Dependencies include Ant Design table/tabs/tooltips, `pretty-ms` for durations, `moment` for refresh time, `ReplicationIcon`, `ColumnSearch`, and Recon axios/autoreload helpers. The backend contract is `/api/v1/pipelines`; the datanode column expects each datanode item to expose `hostName` and `uuid`, although the interface currently declares `datanodes: string[]`.

## Risks and edge cases
The `datanodes` type is inaccurate for the actual renderer, weakening TypeScript coverage. A module-level abort controller has the same multi-instance caveat as other Recon views. `onTabChange` advertises inactive-pipeline behavior but does nothing. `onShowSizeChange` logs to console rather than updating any data-source page size, which is acceptable for client-side tables but noisy in production.

## Test signals
No direct UI test is in this subset. Useful tests would mock `/api/v1/pipelines`, verify column search injection, status filters, datanode tooltip rendering, cancellation on unmount, and formatting for zero/unavailable leader election metrics.
