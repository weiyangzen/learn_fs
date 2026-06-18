# sources/object-store/garage/src/garage/tests/k2v/errorcodes.rs

Purpose: This test verifies that malformed K2V requests return client errors instead of being accepted or misclassified.

Important APIs and types: `test_error_codes` uses `common::context`, `CustomRequester`, Hyper `Method`, and `StatusCode`. It covers PUT, POST search, POST batch insert, and poll-style GET parameters.

Control flow: The test first performs a valid insert and expects 204. It then sends requests with an invalid causality token, missing partition key in search body, start outside prefix, invalid JSON, invalid causality token in batch insert, invalid base64 value in batch insert, and invalid poll causality token. Each invalid request must return 400 Bad Request.

State and persistence behavior: Only the initial valid item is persisted. The invalid operations should not mutate data and are focused on validation/error response behavior.

Dependencies and integration points: It exercises K2V request parsing, causality token decoding, range filter validation, JSON parsing, base64 decoding, and error-to-status mapping.

Risks: It only checks status codes, not response bodies or error codes. The search JSON uses `partition_key` in invalid examples, while other tests use camelCase `partitionKey`, so part of the signal depends on deserialization behavior.

Test signals: Status 204 for the control insert and 400 for every malformed request.
