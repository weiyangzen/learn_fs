# sources/sync-backup/git-lfs/tq/basic_upload.go

Purpose: basic HTTP PUT upload adapter with content-type detection, progress callbacks, retry wrapping, and optional verify action.

Important APIs/types/functions: `BasicAdapterName`, `defaultContentType`, `basicUploadAdapter`, `DoTransfer`, `setContentTypeFor`, `startCallbackReader`, `newStartCallbackReader`, `configureBasicUploadAdapter`, and `makeRequest`.

Control flow: obtains upload action, builds PUT request, sets content length unless chunked, opens local file, detects content type unless disabled, wraps body with progress callback and auth-start callback, executes request, maps network/429/403 errors to retriable variants, validates status, drains response body, and calls `verifyUpload`.

State and persistence: reads local object file; no durable writes. Progress body can reset progress on retry.

Dependencies and integration points: registered as `basic` upload adapter; used by `TransferQueue`. Depends on `lfsapi`, `tools.NewFileBodyWithCallback`, URL config, and verify logic.

Risks: recursive auth retry reopens the file and assumes open succeeds (`f, _`). Content-type detection rewinds the file and can fail. HTTP 422 is deliberately non-retriable to trigger content-type guidance.

Test signals: upload behavior is not directly tested here; verify action has separate tests.
