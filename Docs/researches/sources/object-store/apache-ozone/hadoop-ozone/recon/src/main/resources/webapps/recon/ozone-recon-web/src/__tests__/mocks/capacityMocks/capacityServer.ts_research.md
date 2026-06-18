# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityServer.ts


Purpose: MSW server for Capacity page tests.

Important APIs/types/functions: Creates `handlers` for `api/v1/storageDistribution` and `api/v1/pendingDeletion`, then exports `capacityServer = setupServer(...handlers)`.

Control flow/state/persistence: The pending deletion handler branches on query param `component` and returns SCM, OM, DN, or 400 unsupported responses.

Dependencies/integration points: Consumed by `Capacity.test.tsx`; provides the main API surface for capacity data and pending deletion breakdown.

Risks/test signals: Uses relative paths without leading slash (`api/v1/...`), matching the test environment’s request style. Unsupported component behavior is present but not directly asserted.
