# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/datanodes.utils.tsx


Purpose: Small Testing Library helper for waiting on the datanode table.

Important APIs/types/functions: Exports `waitForDNTable`, returning `waitFor(() => screen.getByTestId('dn-table'))`.

Control flow/state/persistence: No state. It wraps an async polling assertion in a reusable function.

Dependencies/integration points: Used by datanode page and table tests; depends on the V2 datanodes table retaining `data-testid="dn-table"`.

Risks/test signals: Callers must `await` it; one table test currently does not, reducing the helper’s value there.
