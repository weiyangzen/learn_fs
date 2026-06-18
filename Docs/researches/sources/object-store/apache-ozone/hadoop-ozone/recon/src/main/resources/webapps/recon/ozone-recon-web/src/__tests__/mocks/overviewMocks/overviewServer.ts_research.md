# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewServer.ts


Purpose: MSW normal and faulty servers for Overview tests.

Important APIs/types/functions: Defines `handlers`, `faultyHandlers`, `overviewServer`, and `faultyOverviewServer`. Endpoints include `api/v1/clusterState`, `api/v1/task/status`, `api/v1/keys/open/summary`, and `api/v1/keys/deletePending/summary`.

Control flow/state/persistence: Normal handlers return fixture data; faulty handlers return `null` with HTTP 200 to test UI fallback behavior rather than transport errors.

Dependencies/integration points: Used by `Overview.test.tsx` to assert both populated and `N/A`/zero states.

Risks/test signals: `TaskStatus` must exist in the response mock module. Returning null with 200 is a strong signal that the Overview page should treat schema absence separately from HTTP failure.
