# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/diskUsage/diskUsage.tsx

Purpose: Legacy Namespace Usage/Disk Usage page. It renders a navigable pie chart of namespace usage, supports path input, back/refresh, display-limit selection, and a metadata drawer for the current path.

Important APIs/types/functions: Defines DU response/subpath/plot/state interfaces, constants `DEFAULT_DISPLAY_LIMIT`, `OTHER_PATH_NAME`, `MAX_DISPLAY_LIMIT`, and `MIN_BLOCK_SIZE`, and class methods `handleChange`, `handleSubmit`, `goBack`, `updatePieChart`, `clickPieSection`, `refreshCurPath`, and `showMetadataDetails`. Uses `AxiosGetHelper` against `/api/v1/namespace/usage`, `/api/v1/namespace/summary`, and `/api/v1/namespace/quota`, `cancelRequests`, `EChart`, `DetailPanel`, and `byteToSize`.

Control flow: Mount loads root usage. Submitting a path cancels outstanding requests and calls `updatePieChart`. That method fetches namespace usage, handles `PATH_NOT_FOUND`, slices subpaths to the selected limit, computes an "Other Objects" slice when needed, adds `MIN_BLOCK_SIZE` to nonzero slices for visibility, and stores chart data. Clicking a slice navigates into it unless it is "Other Objects". Metadata fetch starts summary and quota requests in parallel and appends fields to shared key/value arrays before showing the drawer.

State and persistence: Local state stores loading, current response, plot data, drawer visibility/content, normalized return path, input path, and display limit. Module-level cancellation controllers and `valuesWithMinBlockSize` are shared. No browser persistence.

Dependencies and integration points: Integrates with Recon namespace usage, summary, and quota endpoints, Ant Design controls, ECharts wrapper, and legacy right drawer.

Risks: Paths are interpolated without URL encoding. `IDUResponse` is typed as an array in state but used as an object throughout. The synthetic `other` subpath omits required `sizeWithReplica` and `isKey` fields. Summary and quota requests mutate the same `keys`/`values` arrays asynchronously, so drawer order/content can race. The form `onSubmit` does not visibly prevent default. `structuredClone` may be unavailable in older browsers.

Test signals: Tests should cover root load, path submit, invalid path, empty object rendering, limit changes, "Other Objects" calculation, slice navigation, back path calculation, metadata for KEY and non-KEY paths, quota append behavior, and request cancellation.
