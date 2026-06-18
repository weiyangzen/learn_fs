# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/Pipelines.test.tsx


Purpose: Page-level tests for V2 Pipelines covering render, data load, row count, empty data, debounced search, no results, and API error propagation.

Important APIs/types/functions: Uses `Pipelines`, `pipelineServer`, locator constants, `waitForPipelineTable`, and a spy on `showDataFetchError`. Mocks AutoReloadPanel and V2 MultiSelect.

Control flow/state/persistence: Starts MSW once, renders the page, waits for table or rows, changes search input, waits 310 ms for debounce, and overrides `api/v1/pipelines` for empty/error cases.

Dependencies/integration points: Tests the page’s integration with table rows, multi-select/search controls, and common error notification path.

Risks/test signals: Search tests depend on debounce timing. Error expectation is axios-string specific. The “no results” comment mentions datanode, a copy/paste artifact.
