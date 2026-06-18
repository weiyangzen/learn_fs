# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeResponseMocks.ts


Purpose: Datanode API fixture set for V2 datanode page and table tests.

Important APIs/types/functions: Exports `DatanodeResponse`, `NullDatanodeResponse`, `NullDatanodes`, and `DecommissionInfo`.

Control flow/state/persistence: Static JSON-like data. The main response contains five datanodes spanning HEALTHY, STALE, DEAD, DECOMMISSIONING, and DECOMMISSIONED op states, with storage reports, pipeline memberships, version/build info, and rack location.

Dependencies/integration points: Used by `datanodeServer.ts`, page search tests, table row tests, and decommission info UI.

Risks/test signals: Mixed-case hostname `ozone-DataNode-5...` intentionally tests case-sensitive/case-insensitive behavior. Null fixtures are exported for edge-case tests but not used by the primary suite shown.
