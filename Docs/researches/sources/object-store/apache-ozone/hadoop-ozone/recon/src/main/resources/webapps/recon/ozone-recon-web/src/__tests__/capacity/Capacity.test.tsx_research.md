# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/capacity/Capacity.test.tsx


Purpose: Tests the V2 Capacity page’s cluster capacity, pending deletion, datanode detail, and SCM sentinel-error rendering.

Important APIs/types/functions: Renders `Capacity`, uses `capacityServer`, capacity response mocks, and inline MSW override for `api/v1/pendingDeletion?component=scm`. Mocks legacy `AutoReloadPanel` and chart components.

Control flow/state/persistence: Server starts once and resets after each test. Tests render the page, find cards by headings, then assert card-local text content and `pending-deletion-scm-error`.

Dependencies/integration points: Exercises `/api/v1/storageDistribution` and `/api/v1/pendingDeletion` for `scm`, `om`, and `dn`. Integrates with AntD card/table markup and chart count expectations.

Risks/test signals: Uses card DOM traversal with `.closest('.ant-card')`, so AntD markup changes can break tests. Sentinel `-1` handling for SCM is a documented behavior signal that should be preserved.
