# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/capacity.types.ts

Purpose: Defines v2 capacity and utilization API response types for global storage, namespace usage, data-node usage, pending deletion, and chart segments.

Important APIs/types/functions: Important exported types are `DataNodeUsage`, `UtilizationResponse`, `DNPendingDeletion`, `OMPendingDeletion`, `SCMPendingDeletion`, and `Segment`. Internal helper shapes include `GlobalStorage`, `GlobalNamespace`, `UsedSpaceBreakdown`, `OpenKeyBytesInfo`, and `DNPendingDeleteStat`.

Control flow: Type-only module. It encodes nested REST response contracts consumed by capacity components.

State and persistence: No runtime state. Nullable fields in pending deletion types model backend jobs that may not have completed.

Dependencies and integration points: Used by v2 capacity page/components and any chart code requiring segment labels as strings or React nodes. Values map to Recon capacity/utilization endpoints.

Risks: Several internal types are not exported, limiting reuse outside this module. `DNPendingDeletion.status` is a strict union, so backend status additions break typing until updated. `React.ReactNode` is referenced without importing React in modern TS configs that do not provide global React types.

Test signals: Type-checking and API fixture tests should cover complete, in-progress, failed, and null pending deletion responses plus utilization responses with all nested storage fields.
