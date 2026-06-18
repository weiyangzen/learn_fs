# sources/sync-backup/git-lfs/t/cmd/lfstest-customadapter.go

Purpose: test custom transfer adapter that proxies upload/download requests to normal LFS storage URLs.

Important APIs/types/functions: `main`, `writeToStderr`, `sendResponse`, `sendTransferError`, `sendProgress`, `performDownload`, `performUpload`, and protocol structs `request`, `action`, `transferResponse`, `progressResponse`, `transferError`.

Control flow: reads line-oriented JSON events from stdin. `init` acknowledges; `download` performs authenticated GET to `action.href`, copies to a temp file with progress callbacks, and returns a completion path; `upload` opens the source path, builds an authenticated PUT with headers/content length or chunked transfer, streams with progress callbacks, and returns completion; `terminate` logs.

State/persistence behavior: creates temporary download files and reads upload source files. Network side effects mutate the test LFS server storage.

Dependencies/integration: exercises Git LFS custom transfer adapter protocol, `lfsapi.Client`, and `tools.CopyWithCallback`/`NewBodyWithCallback`.

Risks: if upload auth fails with nil response, `res.StatusCode` can panic in one error path. The terminate case breaks only the switch, so the scanner loop continues until stdin closes.

Test signals: JSON progress/complete events, stderr protocol logs, and server-stored object content.
