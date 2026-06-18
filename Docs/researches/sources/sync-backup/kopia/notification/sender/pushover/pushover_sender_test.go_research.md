# sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_test.go

Purpose: tests Pushover HTTP payloads, error handling, validation, and merge behavior.

Important APIs/types/functions: `TestPushover`, `TestPushover_Invalid`, and `TestMergeOptions`, using `httptest.Server`, `sender.GetSender`, and `pushover.Options`.

Control flow: the main test records requests and bodies from a local server, creates plain and HTML senders, sends two messages, decodes JSON bodies, and asserts token/user/message/html fields. It then exercises non-OK HTTP status and connection failure paths. The invalid test asserts missing token and user key validation. Merge tests verify create and update replacement for app token/user key.

State and persistence behavior: request capture buffers act as test state; no external Pushover service is contacted.

Dependencies/integration points: validates registry construction, endpoint override, JSON body construction, and HTTP response handling. Risks/test gaps include no coverage of real default endpoint, context cancellation, non-JSON marshal failures, custom format update, endpoint merge behavior, or Pushover-specific response bodies. The tests provide strong signals for the current minimal API contract.
