# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/Datanodes.test.tsx


Purpose: Page-level tests for V2 Datanodes, validating initial render, API data load, empty data, debounced search, case behavior, no-result UI, and API error handling.

Important APIs/types/functions: Uses `Datanodes`, `datanodeServer`, `waitForDNTable`, locator constants, and spies `showDataFetchError`. Mocks `AutoReloadPanel` and V2 `multiSelect` to isolate search/table behavior.

Control flow/state/persistence: MSW server starts once. Tests render the page, wait for rows/table, update search input, pause 310 ms for debounce, and check row counts. One removal modal test is skipped because the static mock response never reflects removal.

Dependencies/integration points: Covers `api/v1/datanodes` and `api/v1/datanodes/decommission/info`, plus common error reporting.

Risks/test signals: The debounce sleep is timing-sensitive. Error expectation checks a stringified Axios error, which may change with axios versions.
