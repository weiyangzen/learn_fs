# sources/sync-backup/git-lfs/t/t-batch-storage-upload-tus.sh

## Purpose
Tests TUS protocol upload support through the Git LFS batch API. It validates both fresh uploads and interrupted uploads that resume from a server-reported offset.

## Important APIs, Functions, and Control Flow
Each test uses a repository name that advertises `tus` transfer support, sets `lfs.tusTransfers true`, commits `a.dat` plus `verify.dat`, and pushes with trace/curl verbose output. The normal case expects HEAD and PATCH requests from offset zero and no resume. The interrupted case expects initial 500 responses, repeated HEAD/PATCH requests, resume from one third of each object, and final `204 No Content`.

## State, Persistence, and Dependencies
State includes local Git config, LFS objects, server object storage, and `push.log`. The content string `send-verify-action` triggers verify-action behavior. The tests depend on the test server's TUS implementation and log messages from the TUS adapter.

## Integration Points, Risks, and Test Signals
Integration is with the batch adapter negotiation, TUS upload adapter, verify action, and retry/resume machinery. Signals are `Upload-Offset` counts, `xfer: tus.io` log lines, HTTP status counts, and `assert_server_object`. Risks include exact offset math for tiny objects and tight coupling to trace wording.
