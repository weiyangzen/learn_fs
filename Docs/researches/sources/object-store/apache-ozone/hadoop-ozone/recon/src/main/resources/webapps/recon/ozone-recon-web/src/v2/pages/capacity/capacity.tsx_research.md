# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/capacity.tsx

Purpose: Cluster Capacity page combining storage distribution, SCM/OM/DN pending deletion, per-datanode details, auto-reload, and CSV download readiness polling.

Important APIs, types, and functions: Exports default `Capacity`. Local async helpers are `waitForDnFinished` and `downloadCsv`; derived values include `selectedDNDetails`, status labels, and breakdown descriptors.

Control flow: Fetches storage distribution and three pending-deletion endpoints, refreshes all APIs through auto-reload, adjusts polling interval while DN scans are running, derives cluster/service cards, waits for DN status FINISHED before downloading CSV, and renders `CapacityBreakdown` and `CapacityDetail` cards.

State and persistence behavior: Tracks `lastUpdated` and selected datanode. API state comes from four `useApiData` calls. Auto-reload enabled state is persisted via sessionStorage.

Dependencies: Uses AntD Popover/Tag/Typography/icons, `filesize`, moment, capacity constants/types, capacity subcomponents, `useApiData`, and `useAutoReload`.

Integration points: Consumes `/api/v1/storageDistribution`, `/api/v1/pendingDeletion?component=scm|om|dn`, and `/api/v1/storageDistribution/download`.

Risks and edge cases: CSV polling uses raw `fetch` outside `useApiData` and can run for 10 minutes. The total-capacity popover duplicates `File System Capacity` text. Default DN data can produce unknown host selections. Poll interval restart depends on autoReload object identity and suppressed deps.

Test signals: Cover API loading/errors, DN scan RUNNING versus FINISHED interval, CSV not-ready/content-type/filename handling, selected DN disabled options, SCM negative error path, and capacity math.
