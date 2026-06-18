# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/datanodesTable.tsx

Purpose: Displays datanode inventory, health/op-state, storage usage, pipeline membership, and dead-node row selection for removal.

Important APIs, types, and functions: Exports `DatanodesTable` and mutable `COLUMNS`. Local render helpers map health/op states to icons and pipeline popovers.

Control flow: Filters columns by parent selection, filters rows by selected search field, updates a module-level `decommissioningUuids` from props, and uses AntD rowSelection while disabling checkboxes for non-DEAD nodes.

State and persistence behavior: No local state, but uses module-level `decommissioningUuids` for UUID-column rendering.

Dependencies: Uses AntD table/popover/tooltip/icons, `StorageBar`, `DecommissionSummary`, `ReplicationIcon`, moment utilities, and datanode/pipeline types.

Integration points: Consumed by `pages/datanodes/datanodes.tsx`, which supplies decommission data, selected rows, and removal workflow.

Risks and edge cases: Module global `decommissioningUuids` can leak between component instances/tests. `isSelectable` returns `record.state !== 'DEAD' && true`, which is semantically a disabled predicate but awkward. Search assumes all fields have `includes`.

Test signals: Cover dead-only selectable behavior, decommission summary display, pipeline leader icon, storage report rendering, search by hostname/uuid/version/revision, and test-id row attributes.
