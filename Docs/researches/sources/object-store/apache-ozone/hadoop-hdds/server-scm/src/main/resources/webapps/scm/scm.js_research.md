# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/resources/webapps/scm/scm.js

Purpose: This AngularJS module powers the SCM web UI pages for overview and Ratis events. It fetches JMX beans from SCM, transforms node, pipeline, container, and Ratis metrics into view-model state, and implements client-side search, pagination, and custom sorting for the node table.

Important APIs and types: The file defines module `scm` with dependencies `ozone` and `nvd3`, configures the `/ratis_events` route, registers `ratisEvents`, and registers `scmOverview`. The overview controller uses `$http`, `$scope`, and `$sce`, and reads JMX queries for `StorageContainerManager,name=SCMMetrics`, `SCMNodeManagerInfo`, `SCMPipelineManagerInfo`, and `ReplicationManagerMetrics`.

Control flow: `ratisEvents` fetches SCMMetrics, splits `tag.RatisEvents` by newline and pipe, and exposes timestamp/description objects. `scmOverview` initializes placeholder statistics, fetches Ratis role information, fetches node manager JMX data, maps `NodeStatusInfo` entries into table rows, derives per-node UI protocol and port from the browser scheme and JMX port entries, updates node usage/state/space statistics, fetches pipeline counts, fetches container lifecycle and health counts, and exposes UI functions for global search, records-per-page changes, page navigation, current item ranges, column sort toggling, and custom op-state/health-state sort order.

State and persistence behavior: All state is browser runtime state stored in controller fields and `$scope`. There is no persistence. `nodeStatusCopy` keeps the full fetched node list while `$scope.filteredNodes` and `$scope.nodeStatus` hold filtered and paginated views. The UI trusts selected JMX fields and uses `$sce.trustAsHtml` in `formatValue`.

Dependencies and integration points: It integrates the static SCM web app with the HTTP server, JMX JSON endpoint, SCM MXBeans and metrics naming, Ratis metrics, SCMNodeManager node-status schema, pipeline manager schema, and replication manager metrics. It depends on templates `scm-overview.html` and `ratis-events.html`.

Risks: Many mappings assume `result.data.beans[0]` exists and that `value.find(...)` returns an object; missing JMX fields can throw. `formatValue` uses `value.replace('/;/g', '<br>')`, which passes a string rather than a regex and likely does not replace semicolons globally. `$sce.trustAsHtml` should be limited to trusted JMX values. Pagination first-item display returns 1 even for empty results, while last index is clamped to at least 1. Ratis event parsing assumes `timestamp|description` format and ignores extra separators.

Test signals: UI tests should mock JMX responses for normal and missing-field cases, verify protocol/port fallback from HTTP/HTTPS, node statistics mapping, search across all row fields, pagination including empty results and "All", custom state ordering, container/pipeline count rendering, and Ratis event parsing.
