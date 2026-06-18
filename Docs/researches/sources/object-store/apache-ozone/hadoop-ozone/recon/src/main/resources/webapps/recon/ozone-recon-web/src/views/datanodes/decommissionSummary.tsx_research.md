# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/decommissionSummary.tsx

Purpose: Legacy row-level popover component that fetches and displays decommission details for a datanode UUID.

Important APIs/types/functions: Class component `DecommissionSummary` wrapped with `withRouter`. It uses `axios.get('/api/v1/datanodes/decommission/info/datanode?uuid=...')`, Ant Design `Descriptions`, `Popover`, `Tooltip`, and `InfoCircleOutlined`. Main methods are `componentDidMount`, `fetchDecommissionSummary`, and `render`.

Control flow: On mount, it marks itself loading and fetches summary data for `props.uuid` if local `record` and `summaryData` exist. Successful response selects the first `DatanodesDecommissionInfo` entry. Rendering builds a descriptions panel when summary data has `datanodeDetails`, optionally including metrics and under-replicated/unclosed container lists, and wraps the UUID in a hover popover.

State and persistence: State is initialized from props and later stores `summaryData` and loading flags. No persistent storage. There is no request cancellation on unmount.

Dependencies and integration points: Used by the legacy Datanodes table UUID column when a row is actively decommissioning. Integrates directly with the decommission detail endpoint and shared fetch-error helper.

Risks: Props and state are typed as `string[]` but used as objects with fields such as `datanodeDetails`, causing weak type safety. State sets `loading` while the interface names `isLoading`. No cancellation means unmounted row components can set state after fetch completion. The mount guard checks `summaryData` even though the initial empty array is truthy, so it always fetches when a record exists.

Test signals: Tests should cover successful summary with metrics/containers, empty summary fallback to plain UUID, fetch error notification, and unmount behavior if cancellation is added.
