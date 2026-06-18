# sources/sync-backup/git-lfs/tq/api_test.go

Purpose: tests HTTP batch API encoding/decoding and schema conformance.

Important APIs/types/functions: `TestAPIBatch`, `TestAPIBatchOnlyBasic`, `TestAPIBatchEmptyObjects`, schema globals, `sourcedSchema`, `getSchema`, and `assertSchema`.

Control flow: starts `httptest` servers, validates incoming JSON against request schema, emits schema-valid responses, and checks client results. The init function loads schema files from `schemas/`.

State and persistence: no durable state; creates local test servers and reads schema files.

Dependencies and integration points: uses `gojsonschema`, `lfsapi`, and `lfshttp`; ties tests to `http-batch-*.json`.

Risks: content-length assertion in one test is sensitive to JSON encoding changes. Schema loading failures print rather than fail until tests require non-nil schema.

Test signals: good coverage for request transfer-list behavior and schema contract.
