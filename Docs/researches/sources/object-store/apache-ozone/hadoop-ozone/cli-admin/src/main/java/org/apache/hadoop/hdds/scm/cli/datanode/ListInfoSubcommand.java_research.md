# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/ListInfoSubcommand.java

## Purpose
Implements `ozone admin datanode list`, listing datanode state, pipeline associations, volume health, and optionally usage-enriched ordering.

## Important APIs, Types, And Functions
Options include operational/health state filters, `--json`, `--nodes-with-failed-volumes`, node selection through `ExclusiveNodeOptions`, `--most-used/--least-used`, and `ListLimitOptions`. It uses `BasicDatanodeInfo`, `ScmClient.listPipelines`, `queryNode`, and `getDatanodeUsageInfo`.

## Control Flow
The command rejects failed-volume filtering with node ID lookup, loads pipelines, handles single UUID lookup, otherwise streams all nodes or sorted usage info, applies IP/hostname/state/failed-volume filters, limits results unless `--all`, and prints JSON or text details with related pipelines.

## State And Persistence
Read-only against SCM node, pipeline, and usage state. It stores the pipeline list for text rendering.

## Dependencies And Integration Points
Depends on `NodeSelectionMixin`, `BasicDatanodeInfo`, SCM node/usage/pipeline APIs, `JsonUtils`, and shell `ListLimitOptions`.

## Risks And Test Signals
UUID parsing can throw for invalid IDs. Usage-sorted mode performs one `queryNode` per returned usage entry. Tests should cover all filters, limits, JSON/text, failed volume output, most/least used ordering, invalid UUID, and nodes with no related pipelines.
