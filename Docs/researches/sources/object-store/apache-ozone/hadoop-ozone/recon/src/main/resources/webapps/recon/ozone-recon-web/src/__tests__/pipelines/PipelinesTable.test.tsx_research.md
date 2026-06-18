# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/PipelinesTable.test.tsx


Purpose: Component tests for V2 `PipelinesTable`, validating render, search filtering, dynamic selected columns, sorting, and pagination.

Important APIs/types/functions: Defines `defaultProps` and `getPipelineWith`, imports `Pipeline` and `PipelinesTableProps`, mocks AntD `scrollTo`, and uses `pipelineLocators`.

Control flow/state/persistence: Renders controlled data arrays, simulates header clicks for sorting, and clicks pagination next page for an 11-row data set.

Dependencies/integration points: Exercises AntD table sorting/pagination and the table’s selected-column projection.

Risks/test signals: Pagination test catches and suppresses `ReferenceError`, which can hide real failures. Sorting expectations depend on default AntD sort direction after one header click.
