# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelineResponseMocks.ts


Purpose: Pipeline API fixture for V2 pipeline page tests.

Important APIs/types/functions: Exports `PipelinesResponse` with `totalCount` and three visible pipeline records in the file content read, each including pipeline id, status, leader, datanodes, timing/election fields, replication type/factor, and container count.

Control flow/state/persistence: Static fixture only. Datanode entries include rich backend node details, ports, network info, and persisted op state, even though table tests mostly assert pipeline fields.

Dependencies/integration points: Consumed by `pipelinesServer.ts` and page tests.

Risks/test signals: `totalCount` says 6 while the fixture contains 3 records, which tests codify by expecting 3 rows. That mismatch can mask pagination/count behavior if the table later uses `totalCount`.
