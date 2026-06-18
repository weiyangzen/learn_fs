# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeServer.ts


Purpose: MSW servers for datanode tests, including normal and null-response variants.

Important APIs/types/functions: Exports `datanodeServer`, `nullDatanodeResponseServer`, and `nullDatanodeServer`; handlers cover `api/v1/datanodes` and `api/v1/datanodes/decommission/info`.

Control flow/state/persistence: Each server uses a different datanode payload while sharing decommission info. No mutable state beyond MSW server lifecycle.

Dependencies/integration points: Primary suite uses `datanodeServer`; null servers are ready for robustness tests around partially null payloads.

Risks/test signals: Like other mocks, paths are relative. Decommission endpoint shape must remain consistent with V2 datanode summary consumers.
