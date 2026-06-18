# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewResponseMocks.ts


Purpose: Overview dashboard fixture values for health, capacity, and key summaries.

Important APIs/types/functions: Exports `ClusterState`, `OpenKeys`, and `DeletePendingSummary`. `overviewServer.ts` also references `TaskStatus`, so this fixture file is expected to define or re-export it in the current tree state; if absent, tests/build would fail.

Control flow/state/persistence: Static data only. Values map directly to expected Overview cards: datanodes `3/5`, containers `20`, volumes `2`, buckets `24`, keys `1424`, pipelines `7`, and byte summaries.

Dependencies/integration points: Consumed by overview MSW handlers and `Overview.test.tsx`.

Risks/test signals: Missing or renamed exports are caught at test compile time. Byte values are chosen to exercise filesize rendering (`1 KB`, `4 KB`, etc.).
