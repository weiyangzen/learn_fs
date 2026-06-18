# Research: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/db.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008126`: lines 1-9035, `Docs/researches/chunks/subset-b-008126_research.md`
- `subset-b-008127`: lines 9036-9231, `Docs/researches/chunks/subset-b-008127_research.md`

## Chunk Research

### subset-b-008126: lines 1-9035

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/db.json lines 1-9035

## Chunk Scope

This chunk covers the mock Recon web API database from the beginning of `db.json` through line 9035. It includes every top-level fixture from `clusterState` through the beginning of the standalone `DatanodesDecommissionInfo` response. The physical source file continues to line 9230 with the rest of `DatanodesDecommissionInfo`, `datanodesRemove`, `utilization`, and pending-deletion summaries, so this chunk should be merged with the following chunk before producing a final whole-file report.

## Purpose

`db.json` is not executable application code; it is the data backing the Recon UI mock API server. The web app's `package.json` runs `json-server --watch api/db.json --routes api/routes.json --middlewares api/pagination.js --port 9888`, so each top-level JSON key acts like a resource table or endpoint response. `api/routes.json` maps real-looking Recon paths such as `/api/v1/clusterState`, `/api/v1/datanodes`, `/api/v1/containers/unhealthy/MISSING*`, `/api/v1/namespace/usage?...`, `/api/v1/keys/open/summary`, and `/api/v1/datanodes/decommission/info` onto these top-level keys.

The fixtures provide broad UI coverage for Overview, Datanodes, Pipelines, Namespace, Containers, Volumes/Buckets, Heatmap, Open/Delete Pending Keys, Container Mismatch, Decommissioning, and Capacity views. They intentionally include normal records, empty responses, pagination cursors, large numeric identifiers, negative sentinel values, nulls, and count/data mismatches to exercise client rendering behavior.

## Important Data APIs and Shapes

The top-level resources visible in this chunk include:

- `clusterState`: summary counts for pipelines, datanodes, storage, containers, volumes, buckets, keys, deletion backlog, and SCM/OM service IDs.
- `datanodes`: `{ totalCount, datanodes }` with 19 datanode rows. Rows include host/UUID, health `state`, operational `opState`, heartbeat/setup timestamps, storage reports, pipeline summaries, container/open-container counts, leader counts, version, revision, and build date.
- `pipelines`: `{ totalCount, pipelines }` with 3 pipeline rows. Pipeline rows include id, status, leader, datanode network details and ports, election timing, replication type/factor, and container count.
- `missingContainers` and `keys`: older container/key listing fixtures. `keys` contains volume/bucket/key names, data sizes, versions, block maps keyed by version, and ISO creation/modification times.
- `fileSizeCounts` and `containerCount`: histogram-like arrays for utilization pages.
- Namespace browser fixtures `root`, `volume`, `bucket`, `dir`, `empty`, `key`, `clunky`, and `replica`: all use the same usage response shape with `status`, `path`, `size`, `sizeWithReplica`, `subPathCount`, `subPaths`, and `sizeDirectKey`.
- `metadata` and `quota`: namespace summary/quota responses. `metadata.objectInfo` mirrors Ozone object metadata, including ACLs, key location versions, replication config, bucket layout, owner, object IDs, and file/key attributes.
- `taskStatus`: Recon task status rows for container-key mapping, file-size counting, table count, namespace summary, OM delta/snapshot, container health, and pipeline sync tasks.
- Unhealthy container fixtures: `unhealthyContainers`, `unhealthyMissing`, `unhealthyUnderReplicated`, `unhealthyOverReplicated`, `unhealthyMisReplicated`, and `unhealthyReplicaMismatch`. These expose aggregate unhealthy counts, cursor fields, and container arrays with replica details.
- Object inventory and visualization fixtures: `volumes`, `buckets`, `bucketHeatmap`, `keyHeatmap`, and `heatmap`.
- Feature and overview summaries: `disabledFeatures`, `keysOpenSummary`, and `keysdeletePendingSummary`.
- Container mismatch fixtures: `omMismatch` and `scmMismatch`, each with `containerDiscrepancyInfo` rows, pipeline replication config, health flags, and `existsAt` markers.
- Open-key and pending-delete fixtures: `nonFSO`, `fso`, `keydeletePending`, `deleted`, and `dirdeletePending`.
- Decommission fixtures: `decommissioninfo` and the start of `DatanodesDecommissionInfo`. They use a capitalized `DatanodesDecommissionInfo` array property, matching current UI consumers.

## Control Flow and Serving Behavior

`db.json` itself has no functions or control flow. Runtime behavior is supplied by `json-server`, `routes.json`, and `pagination.js`.

`routes.json` first maps specific unhealthy-container subtype paths to subtype fixtures, then maps `/api/v1/*` to `/$1`, then adds more query-specific rewrites. This means route order matters: a specific query route such as `/keys/open?includeFso=false&includeNonFso=true&limit=*` resolves to `/nonFSO`, while generic API resources such as `/api/v1/datanodes` resolve to `/datanodes`.

For unhealthy subtype endpoints, `pagination.js` reads `db.json` on each matching request after `json-server` has already rewritten the path. It maps `/unhealthyMissing`, `/unhealthyUnderReplicated`, `/unhealthyOverReplicated`, `/unhealthyMisReplicated`, and `/unhealthyReplicaMismatch` back to the corresponding top-level key, filters `containers` by `containerID > minContainerId`, sorts ascending, slices to `limit`, and returns updated `firstKey` and `lastKey` values with the aggregate counts. The static `firstKey`/`lastKey` fields stored in `db.json` therefore serve as fallback/default fixture values, but middleware recomputes them for paged subtype requests.

## State and Persistence Behavior

The mock server's persistence is file-backed. `json-server --watch api/db.json` keeps the fixture file as the source of truth and may allow writes for non-GET requests depending on json-server behavior. The `datanodesRemove` fixture gives `/datanodes/remove` a response body containing `selectedRowKeys`, but the route is backed by static JSON rather than real Recon state mutation. Any edits to this file change local mock API state for all developers and tests that use the mock server.

Several fields encode backend state machines or long-running Recon state:

- Datanodes cover `state` values such as `HEALTHY` and `DEAD`, plus `opState` values such as `IN_SERVICE`, `DECOMMISSIONING`, `DECOMMISSIONED`, `ENTERING_MAINTENANCE`, and `IN_MAINTENANCE`.
- Unhealthy containers cover `MISSING`, `UNDER_REPLICATED`, `OVER_REPLICATED`, `MIS_REPLICATED`, and `REPLICA_MISMATCH`, with replica counts, deltas, BCS IDs, and optional checksum data.
- Open key fixtures distinguish non-FSO and FSO layouts; FSO keys use large negative object-ID path segments, while non-FSO uses readable S3-style paths.
- Delete-pending fixtures model grouped key deletion (`deletedKeyInfo` with `omKeyInfoList`), deleted container mismatch records, and deleted directories.
- Decommission fixtures expose datanode details, null metrics for summary rows, and detailed metrics/container categories for a single datanode view.

## Dependencies and Integration Points

Direct dependencies:

- `json-server` consumes this file as a mock database.
- `api/routes.json` defines endpoint-to-resource rewrites for nearly every top-level key.
- `api/pagination.js` depends on the unhealthy subtype keys and the `containers[*].containerID` field.

Observed UI consumers include:

- Overview pages reading `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, `/api/v1/keys/deletePending/summary`, and `/api/v1/datanodes/decommission/info`.
- Datanodes pages reading `/api/v1/datanodes`, `/api/v1/datanodes/decommission/info`, `/api/v1/datanodes/decommission/info/datanode?uuid=...`, and `/api/v1/datanodes/remove`.
- Pipelines and container tables consuming pipeline/datanode/replica shapes.
- Capacity pages consuming `/api/v1/storageDistribution` and `/api/v1/pendingDeletion?...` resources, partly outside this chunk.
- Heatmap and namespace pages consuming the namespace usage, metadata, quota, and read-access heatmap fixtures.

The JSON schema is implicit. TypeScript interfaces in the UI and MSW tests act as the practical contract, so field renames in this fixture can silently break local development even when no Java/Recon backend code changes.

## Risks and Edge Cases

- The chunk ends before the standalone `DatanodesDecommissionInfo` object closes. A chunk-local parser cannot validate only lines 1-9035 as complete JSON; whole-file validation is needed during merge.
- Field spelling and capitalization are contract-sensitive. The fixture uses `DatanodesDecommissionInfo` as both a top-level resource key and response property, and also includes inconsistent spellings such as `decomissioned` in pipeline datanode details versus `decommissioned` in decommission details.
- Count fields do not always match array sizes. For example `unhealthyContainers` reports `missingCount: 3`, `underReplicatedCount: 2`, `overReplicatedCount: 2`, and `misReplicatedCount: 2` while its array contains 10 mixed-state rows including `REPLICA_MISMATCH`. This is useful for UI testing but risky if client code assumes strict arithmetic consistency.
- Some fixture values are deliberately sentinel or unusual: `sizeWithReplica: -1`, pending block sizes of `-1`, null metrics, empty replica arrays for missing containers, huge negative object IDs, very large byte counts, and stringified object descriptions.
- Route matching is brittle because many `routes.json` entries include exact query-string patterns and inconsistent casing such as `sortSubpaths` versus `sortSubPaths`. Small client query changes may bypass the intended fixture.
- `pagination.js` rereads `db.json` per request. This is simple and accurate for watched local data, but malformed JSON or a transient partial edit causes middleware fallback with only a console error.
- The file mixes old and newer API shapes, including legacy top-level resources and v2 UI needs. Removing apparently duplicated sections can break older views, newer pages, or tests.

## Test Signals

Useful validation signals for this chunk:

- `jq` can parse the whole `db.json` file, confirming valid full-file JSON despite the chunk boundary.
- `jq 'keys'` shows all expected top-level resources, including the resources mapped in `routes.json`.
- Array/count checks show major collection sizes: `datanodes` 19, `pipelines` 3, `missingContainers` 2, `keys` 15, unhealthy subtype arrays 25/15/12/13/11, `volumes` 5, `buckets` 5, `omMismatch` 22, `scmMismatch` 50, `nonFSO` 10, `fso` 10, `keydeletePending` 12 groups, `deleted` 32 containers, `dirdeletePending` 5, and `decommissioninfo` 2 rows.
- Mock-server smoke tests should request representative mapped paths: `/api/v1/clusterState`, `/api/v1/datanodes`, `/api/v1/containers/unhealthy/MISSING?limit=5&minContainerId=0`, `/api/v1/namespace/usage?path=/&files=true&sortSubpaths=true`, `/api/v1/keys/open/summary`, `/api/v1/containers/mismatch?&missingIn=OM`, `/api/v1/keys/deletePending?limit=10`, and `/api/v1/datanodes/decommission/info`.
- UI tests around Datanodes, Overview, Pipelines, Containers, Capacity, and namespace browsing are the best regression indicators because they assert the implicit fixture contract more directly than JSON validation alone.

### subset-b-008127: lines 9036-9231

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/db.json lines 9036-9231

## Scope And Purpose

This chunk covers the tail of the Recon web mock API database. It closes the final decommission-information datanode object, then defines mock response bodies for datanode removal, storage distribution, and pending-deletion capacity endpoints:

- `datanodesRemove`, mapped from `/datanodes/remove`.
- `utilization`, mapped from `/storageDistribution`.
- `pendingDeletionDN`, mapped from `/pendingDeletion?component=dn&limit=*`.
- `pendingDeletionOM`, mapped from `/pendingDeletion?component=om`.
- `pendingDeletionSCM`, mapped from `/pendingDeletion?component=scm`.

The file is data, not executable source. Its purpose is to give the local JSON mock server stable payloads that look like Recon backend API responses so the React UI can be developed and manually exercised without a live Ozone cluster.

## Important API Shapes And Fields

The first visible section, lines 9036-9077, finishes a decommission-info datanode entry. It includes topology fields such as `hostNameAsByteString`, `networkName`, `networkLocation`, `networkFullPath`, `numOfLeaves`, and byte-string wrappers with `validUtf8` and `empty` flags. It also includes decommission metrics:

- `decommissionStartTime`
- `numOfUnclosedPipelines`
- `numOfUnderReplicatedContainers`
- `numOfUnclosedContainers`
- `containers.UnderReplicated`
- `containers.UnClosed`

`datanodesRemove` is a minimal response body with `selectedRowKeys`, containing one selected datanode UUID. The frontend datanodes page sends a `PUT` to `/api/v1/datanodes/remove`; in mock mode this fixture acts as the route target for the removal call.

`utilization` is the main storage-distribution response. Its shape matches `UtilizationResponse` in `src/v2/types/capacity.types.ts`:

- `globalStorage`: filesystem capacity, reserved space, derived Ozone capacity, Ozone free/used/committed space.
- `globalNamespace`: total used namespace space and key count.
- `usedSpaceBreakdown`: open key bytes and finalized key bytes.
- `dataNodeUsage`: one record per datanode with UUID, host, capacity, used, remaining, committed, minimum free space, and reserved space.

`pendingDeletionDN` matches the datanode pending-deletion contract:

- `status`: here `FINISHED`, which lets the capacity page stop showing the DN scan as in progress.
- `totalPendingDeletionSize`: aggregate pending deletion bytes.
- `pendingDeletionPerDataNode`: per-datanode pending block size records.
- `totalNodesQueried` and `totalNodeQueriesFailed`: scan coverage metadata.

Two per-datanode entries have `pendingBlockSize: -1`. The v2 capacity page treats this as an error/unavailable sentinel by disabling those datanode options in the selector. The other entries carry concrete byte values used in charts and detail breakdowns.

`pendingDeletionOM` provides `totalSize`, `pendingDirectorySize`, and `pendingKeySize`. `pendingDeletionSCM` provides `totalBlocksize`, `totalReplicatedBlockSize`, and `totalBlocksCount`. These are read by the capacity page's "Pending Deletion" service breakdown.

## Control Flow And Integration

There is no in-file control flow, but the surrounding mock server routing gives this data request flow:

1. `api/routes.json` maps incoming API paths to top-level keys in `api/db.json`.
2. A request for `/api/v1/storageDistribution` resolves to the `utilization` object in this chunk.
3. Requests for `/api/v1/pendingDeletion?component=om`, `/api/v1/pendingDeletion?component=scm`, and `/api/v1/pendingDeletion?component=dn&limit=15` resolve to the three pending-deletion fixtures.
4. The v2 capacity page loads these objects through `useApiData`, combines their numeric fields, and renders utilization and pending-deletion cards.
5. The datanodes pages call `/api/v1/datanodes/remove` through a PUT helper or `useApiData` mutation path; the fixture provides a selected-row echo-like response.

The capacity page uses this data in several derived calculations. It computes "other used space" from Ozone capacity, free space, and used space; displays `totalOzoneCommittedSpace` as container pre-allocated space; sums OM, SCM, and DN pending deletion values; and merges `dataNodeUsage` with `pendingDeletionPerDataNode` by `hostName` for the selected datanode detail view.

## State And Persistence Behavior

The chunk is static JSON persisted in the repository. It does not mutate itself and has no runtime state. Any apparent state, such as `status: "FINISHED"` or `selectedRowKeys`, is fixed mock state returned by the local development API layer.

The persistence contract is still important because consumers assume stable field names and numeric units. The capacity UI treats values as byte counts and formats them for display. The datanode pending-deletion response also models a partially successful scan: `totalNodesQueried` is `7`, `totalNodeQueriesFailed` is `2`, and two datanodes use `-1` as the per-node unavailable sentinel. This lets mock mode exercise both successful and failed datanode pending-deletion paths without backend state transitions.

## Dependencies

Direct dependencies are data-shape dependencies rather than imports:

- `api/routes.json` must keep route-to-key mappings aligned with the top-level keys defined here.
- `src/v2/types/capacity.types.ts` defines the expected TypeScript shapes for storage distribution and pending-deletion responses.
- `src/v2/pages/capacity/capacity.tsx` consumes `utilization`, `pendingDeletionDN`, `pendingDeletionOM`, and `pendingDeletionSCM`.
- `src/v2/pages/datanodes/datanodes.tsx` and the older `src/views/datanodes/datanodes.tsx` consume the datanode remove endpoint.
- Capacity tests under `src/__tests__/capacity` and mock response files under `src/__tests__/mocks/capacityMocks` provide independent test payloads that overlap with these contracts.

The values also depend on Ozone Recon API conventions: SCM, OM, and datanode pending deletion are exposed as separate component-filtered queries, while storage distribution combines global and per-datanode capacity data.

## Risks And Maintenance Notes

The `globalStorage` object in this fixture omits `totalMinimumFreeSpace`, while `GlobalStorage` in `capacity.types.ts` declares it as required. Current capacity rendering paths may not read it, but this is a contract drift risk for future UI changes or stricter validation.

`totalOzoneCommittedSpace` is formatted without a space after the colon (`"totalOzoneCommittedSpace":1022024`). This is valid JSON, but it is inconsistent with the rest of the file and can make generated diffs noisier.

The DN pending-deletion fixture intentionally includes `pendingBlockSize: -1` sentinel values. That is useful for UI coverage, but any consumer that sums per-node values directly instead of using `totalPendingDeletionSize` would undercount. The capacity page currently uses the aggregate total for global DN pending deletion and the sentinel list to disable unavailable selector options.

The `pendingDeletionSCM` field name `totalBlocksize` uses a lowercase `s`, matching the TypeScript type. Renaming it to the more conventional `totalBlockSize` in only one layer would silently break mock-mode display.

The route for DN pending deletion in `routes.json` only matches `/pendingDeletion?component=dn&limit=*`. The v2 capacity page also defines a status URL `/api/v1/pendingDeletion?component=dn` for CSV download polling. If the mock route layer does not have broader matching elsewhere, that polling path may not resolve to this fixture in local mock mode.

The mock values use repeated identical capacities and usage numbers across datanodes. That keeps screenshots predictable, but it gives weak coverage for sorting, scaling, skewed capacity, and high-variance chart behavior.

The `datanodesRemove` object echoes `selectedRowKeys` but does not model failure, partial removal, server-side validation, or asynchronous decommission state changes. UI code that looks correct against this fixture may still need live-backend or MSW tests for real mutation outcomes.

## Test Signals

Useful validation signals for this chunk are mostly frontend and mock-route checks:

- Start the Recon web mock API and verify `/api/v1/storageDistribution` returns the `utilization` object with global storage, namespace, used-space breakdown, and seven datanode usage records.
- Verify `/api/v1/pendingDeletion?component=om`, `/api/v1/pendingDeletion?component=scm`, and `/api/v1/pendingDeletion?component=dn&limit=15` return the expected component-specific payloads.
- Render the v2 capacity page and confirm it shows container pre-allocated space from `totalOzoneCommittedSpace`, pending deletion totals from OM/SCM/DN payloads, and disabled datanode options for entries with `pendingBlockSize: -1`.
- Exercise the capacity CSV download path in mock mode; specifically check whether `/api/v1/pendingDeletion?component=dn` resolves, since the visible mock route only covers the DN query when a `limit` parameter is present.
- Exercise `/api/v1/datanodes/remove` from the datanodes page and confirm the success path reloads data and clears selected rows.
- Keep the existing capacity tests aligned with this fixture's response shapes, especially `DNPendingDeletion.status`, nullable aggregate fields, and the SCM `totalBlocksize` spelling.
