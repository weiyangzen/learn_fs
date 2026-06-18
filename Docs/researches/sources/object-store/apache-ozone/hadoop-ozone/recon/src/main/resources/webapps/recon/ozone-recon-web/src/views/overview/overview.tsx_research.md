# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/overview/overview.tsx

## Purpose
This React class component renders the Recon Overview dashboard. It aggregates cluster state, OM sync task status, open-key summary, pending-delete summary, and decommissioning datanode information into `OverviewCard` tiles, with an `AutoReloadPanel` controlling refresh and OM DB sync.

## Important APIs, types, and functions
`IClusterStateResponse` models `/api/v1/clusterState`; `IOverviewState` stores card values, loading state, timestamps, OM sync status, service IDs, and summary counters. `_loadData` is the main fetch routine and uses `PromiseAllSettledGetHelper` for `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, `/api/v1/keys/deletePending/summary`, and `/api/v1/datanodes/decommission/info`. `omSyncData` calls `/api/v1/triggerdbsync/om`. `componentDidMount` starts polling; `componentWillUnmount` stops polling and aborts pending requests.

## Control flow, state, and persistence
The component keeps all view state in React memory; there is no browser persistence. `_loadData` marks `loading`, cancels previous overview and OM sync requests, then evaluates settled responses. Rejected non-cancel responses produce per-request `showDataFetchError` messages; canceled responses are rethrown as `CanceledError`. Missing cluster state falls back to `N/A` values. Render derives error flags when summary fields are `undefined`, builds health/error UI for datanodes and containers, formats capacity with `filesize.partial`, and routes cards to Recon subpages.

## Dependencies and integration points
The component depends on Ant Design layout/tooltips/icons, `moment`, `filesize`, `OverviewCard`, `AutoReloadPanel`, `AutoReloadHelper`, and Recon axios helpers. It integrates with backend endpoints that are also tested in this subset, especially `ClusterStateEndpoint` and OM insight summaries. Service IDs from cluster state are surfaced as dashboard cards.

## Risks and edge cases
`cancelOverviewSignal` and `cancelOMDBSyncSignal` are module globals, so concurrent component instances would share cancellation state. `decommissionResponse.value?.data?.DatanodesDecommissionInfo.length` assumes the list property exists whenever `data` exists. Casting `missingContainersCount as number` when it may be string `N/A` relies on surrounding checks. `clusterCapacity` subtracts `remaining` from `capacity`; invalid or string values from the API could produce bad formatting.

## Test signals
There is no direct frontend test in this subset. Backend coverage comes indirectly from `TestClusterStateEndpoint`, deleted/open key endpoint tests elsewhere, and utility tests for the response-producing backend. UI behavior should be covered with a mocked axios/rendering test for partial request failure, cancellation, and `N/A` fallback rendering.
