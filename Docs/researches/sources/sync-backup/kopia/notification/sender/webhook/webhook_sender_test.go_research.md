# sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_test.go

Purpose: tests webhook request construction, validation, error paths, and option merging.

Important APIs/types/functions: `TestWebhook`, `TestWebhook_Failure`, `TestWebhook_InvalidURL`, `TestWebhook_InvalidURLScheme`, `TestWebhook_InvalidMethod`, and `TestMergeOptions`, using `httptest.Server`.

Control flow: the main test records two local HTTP requests: a POST with configured and message headers plus markdown-like body, and a PUT with HTML content type. It asserts method, subject, headers, body, summary content, and 404 error handling. Additional tests cover connection failure, bad endpoint syntax, bad scheme, and invalid method rejected during `Send`. Merge tests verify create and update modes.

State and persistence behavior: request slices and body buffers are local test state; no external webhook is contacted.

Dependencies/integration points: validates the sender registry, option validator, `http.NewRequestWithContext`, and message-header overriding behavior. Risks/test gaps include no context cancellation test, no malformed option-header line test, no multi-value header behavior, and no non-200 success variants such as 201/204. Exact body/header assertions provide good regression coverage for the current contract.
