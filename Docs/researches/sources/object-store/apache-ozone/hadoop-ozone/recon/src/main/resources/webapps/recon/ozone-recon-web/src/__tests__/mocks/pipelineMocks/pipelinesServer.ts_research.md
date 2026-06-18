# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelinesServer.ts


Purpose: MSW server for V2 Pipelines tests.

Important APIs/types/functions: Defines one handler for `api/v1/pipelines` returning `PipelinesResponse`, and exports `pipelineServer`.

Control flow/state/persistence: No branching; tests override the handler for empty and error cases.

Dependencies/integration points: Used by `Pipelines.test.tsx` server lifecycle and API override checks.

Risks/test signals: Relative endpoint path must match axios/fetch calls in tests. Because only one default handler exists, additional pipeline endpoints require explicit test additions.
