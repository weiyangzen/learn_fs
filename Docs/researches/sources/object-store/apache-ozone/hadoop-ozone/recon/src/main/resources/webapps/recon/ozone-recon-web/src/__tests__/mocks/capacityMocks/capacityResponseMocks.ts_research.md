# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityResponseMocks.ts


Purpose: Static payloads for V2 Capacity tests.

Important APIs/types/functions: Exports `StorageDistribution`, `ScmPendingDeletion`, `OmPendingDeletion`, and `DnPendingDeletion` with byte/count fields used by capacity cards and charts.

Control flow/state/persistence: No behavior; data fixtures only. Values are deliberately small powers of two so UI renders predictable `KB` labels.

Dependencies/integration points: Consumed by `capacityServer.ts` and by inline test handler overrides. Mirrors backend API shapes for `/api/v1/storageDistribution` and `/api/v1/pendingDeletion`.

Risks/test signals: Fixture field names are an implicit contract with the capacity page. Sentinel failure values are not here, but tests override SCM with `-1` fields, signaling separate error handling logic.
