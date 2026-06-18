# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/DatanodesTable.test.tsx


Purpose: Component-level tests for `DatanodesTable`, focused on rendering, client filtering, row selection rules, and storage tooltip content.

Important APIs/types/functions: Defines `defaultProps` and `getDataWith`, imports `DatanodeTableProps`, `DatanodesTable`, and `waitForDNTable`.

Control flow/state/persistence: Builds synthetic datanode rows with storage reports and pipelines, renders the table with controlled props, then interacts with AntD checkboxes and storage bar hover.

Dependencies/integration points: Integrates with V2 datanode table types, AntD table row selection, `.capacity-bar-v2`, and tooltip labels for filesystem capacity/used/available.

Risks/test signals: Checkbox indexes depend on AntD table DOM order. The first test calls `waitForDNTable()` without awaiting it, so it mostly asserts immediate render. It documents that only DEAD nodes are selectable for removal.
