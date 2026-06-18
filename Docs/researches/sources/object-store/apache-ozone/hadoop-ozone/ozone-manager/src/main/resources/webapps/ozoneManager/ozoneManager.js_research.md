<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/webapps/ozoneManager/ozoneManager.js -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/webapps/ozoneManager/ozoneManager.js

Purpose: AngularJS module for the Ozone Manager web UI pages covering OM metrics, snapshots, Ratis events, overview, and deletion metrics/configuration.

Important APIs/types/functions: Defines module `ozoneManager` with dependencies `ozone` and `nvd3`. Routes map `/metrics/ozoneManager`, `/snapshots`, `/ratis_events`, and `/metrics/deletion` to components. Components include `omSnapshots`, `ratisEvents`, `omMetrics`, `omOverview`, and `omDeletion`. Helpers format bytes and elapsed milliseconds, paginate/sort snapshot diff jobs, and filter ignored JMX keys.

Control flow: Components issue `$http.get` calls to OM servlet endpoints: `jmx` queries for OMMetrics, OmSnapshotInternalMetrics, SnapshotDiffManager, Ratis metrics, deletion metrics, and performance metrics; `snapshotList` for selected volume/bucket snapshots; and `conf?cmd=getPropertyByTag&tags=DELETION` for deletion configs. Results are transformed into controller fields consumed by templates.

State and persistence behavior: No server persistence. Client-side state includes metric arrays, selected pagination fields on `$scope`, snapshot lists, Ratis event arrays, deletion configs, and current role/metrics snapshots.

Dependencies and integration points: Integrates OM webapp templates, JMX servlet output shapes, config servlet output, NVD3 pie charts, D3 formatting, and Angular route/component infrastructure.

Risks: Several handlers assume `result.data.beans[0]` exists; empty JMX responses can break components. Query strings are built by concatenating volume/bucket without encoding. Snapshot diff pagination mixes numeric strings and numbers. Some functions are duplicated across components. Ratis event parsing assumes `timestamp|description` lines.

Test signals: UI tests should mock empty and populated JMX/config responses, verify snapshot list error handling, pagination with `All` and numeric sizes, metric grouping of `Num*Fails`, deletion config sorting, and safe rendering when Ratis or deletion beans are absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/webapps/ozoneManager/ozoneManager.js -->
