# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/pipelinesTable.tsx

Purpose: Displays pipeline inventory with replication, status filters, datanode membership, leader metrics, and duration fields.

Important APIs, types, and functions: Exports `PipelinesTable` and `COLUMNS`. Includes a local `SummaryDatanodeDetails` type until datanode types are shared.

Control flow: Filters columns from parent-selected options, filters rows by `pipelineId` search text, and renders AntD table with tooltips for datanode UUIDs and metrics descriptions.

State and persistence behavior: Stateless.

Dependencies: Uses AntD table/tooltip/icons, `ReplicationIcon`, moment duration utilities, and pipeline types.

Integration points: Consumed by the Pipelines page and receives data from the Recon pipelines API.

Risks and edge cases: Datanode list items lack explicit React keys. Search is only by pipeline ID. The TODO local type can drift from backend/shared datanode type.

Test signals: Cover status filters, replication icon variations, missing leader metrics showing NA, datanode UUID tooltips, selected-column filtering, and row test IDs.
