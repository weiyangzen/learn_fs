# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/pipelines.types.ts

Purpose: Defines v2 pipeline status constants, API response types, page state, and table props.

Important APIs/types/functions: Exports `PipelineStatusList`, `PipelineStatus`, `Pipeline`, `PipelinesResponse`, `PipelinesState`, and `PipelinesTableProps`.

Control flow: Type-only module. Status constants support filters/rendering, while `Pipeline` records leader, datanodes, election timing, replication, and container count.

State and persistence: No runtime state. `PipelinesState` models local table data, column options, and refresh timestamp.

Dependencies and integration points: Imports multi-select `Option`. Used by v2 pipelines page/table and by datanode types for pipeline lists.

Risks: Backend status additions must update `PipelineStatusList`. `replicationType` and `replicationFactor` are plain strings rather than unions. `datanodes` is a string list, so richer datanode metadata is not available at this layer.

Test signals: Tests should include every pipeline status, empty datanode lists, multiple datanodes, missing leader, and table search/column-selection props.
