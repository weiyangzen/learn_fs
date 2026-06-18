# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/pipelines.utils.tsx


Purpose: Testing helper for waiting until the pipelines table exists.

Important APIs/types/functions: Exports `waitForPipelineTable`, returning `waitFor(() => screen.getByTestId('pipelines-table'))`.

Control flow/state/persistence: Stateless async wrapper.

Dependencies/integration points: Used in V2 Pipelines page tests and depends on `PipelinesTable` emitting the expected `data-testid`.

Risks/test signals: This helper only waits for table container presence, not data rows, so callers still need row/text assertions for data-load completeness.
