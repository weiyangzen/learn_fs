# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/insights.types.ts

Purpose: Central v2 type contract for Insights and OM DB Insights data.

Important APIs/types/functions: Exports chart response types (`FileCountResponse`, `ContainerCountResponse`, `PlotResponse`, `FilePlotData`, `ContainerPlotData`, `InsightsState`), mismatch/deleted container types, mismatch key types, replication discriminated union (`RatisInfo`, `EcInfo`, `ReplicationInfo`), open key types, delete-pending key/dir response types, and expanded-row types.

Control flow: Type-only module. The replication union controls rendering logic for RATIS versus EC keys. OM insight responses model multiple endpoints: container mismatch, deleted container keys, open keys, delete-pending keys, delete-pending directories, and container key expansion.

State and persistence: No module state. `InsightsState` and `ExpandedRow` are page-local UI state models.

Dependencies and integration points: Imports v2 multi-select `Option`. Used by v2 insights charts, OM insight page, and insights table components.

Risks: Some backend shapes are very specific and inconsistently named (`Volume`, `Bucket`, `Key` uppercase; `DeletedDirReponse` typo). `MismatchKeys.Blocks` is `Record<string, []>`, losing block detail. `ReplicationInfo` requires checking `replicationType` before accessing RATIS/EC-specific fields. `fileCountError` and `containerSizeError` are strings while hook errors may be objects.

Test signals: Tests should cover RATIS and EC open-key rows, empty and populated file/container distributions, mismatch container expansion, delete-pending key summary aggregation, and typo-sensitive response mapping.
