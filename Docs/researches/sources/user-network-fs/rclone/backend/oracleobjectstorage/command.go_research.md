# sources/user-network-fs/rclone/backend/oracleobjectstorage/command.go

Purpose: implements Oracle Object Storage backend commands exposed through `rclone backend`: `rename`, `list-multipart-uploads`, `cleanup`, and `restore`.

Important APIs: `commandHelp` documents command syntax and options. `(*Fs).Command` dispatches by command name. `rename` validates args, reads object metadata, builds `RenameObjectRequest`, and calls OCI `RenameObject`. `listMultipartUploadsAll`, `listMultipartUploads`, `findLatestMultipartUpload`, `listMultipartUploadsObject`, and `listMultipartUploadParts` enumerate unfinished multipart uploads and parts. `restore` walks filtered objects and calls `RestoreObjects` for archived objects.

Control flow: command dispatch parses option values such as cleanup `max-age` and restore `hours`. Multipart listing either targets the current bucket/prefix from `f.split("")` or lists all buckets then each bucket's uploads. Pagination follows `OpcNextPage`. Exact lookup for resume filters upload objects equal to the requested path and sorts by newest upload. `restore` uses `operations.ListFn`, which may invoke callbacks concurrently, so it protects output accumulation with a mutex and uses a per-object request copy.

State and persistence behavior: `rename` changes object names server-side. `cleanup` aborts pending multipart uploads via main backend cleanup helpers, respecting dry-run/interactive through `operations.SkipDestructive`. `restore` requests temporary restoration from Archive tier and returns per-object statuses. Listing commands only read remote multipart state.

Dependencies and integration points: depends on OCI SDK request/response types, rclone `fs`, `operations`, duration parsing, filters through `operations.ListFn`, and the backend's `split`, `listBuckets`, `cleanUp`, and pacer/client fields. Multipart resume in `multipart.go` depends on `findLatestMultipartUpload` and `listMultipartUploadParts`.

Risks: multipart listing treats a requested object/directory as a prefix for non-exact calls, so paths like `dir` can match `dirKey`. `restore` writes to a shared `err` variable inside concurrent callbacks, which can race logically even though output slice is protected. `rename` returns `fs.ErrorNotAFile` after metadata read failure and logs an extra warning if the object path appears to include the bucket name. Commands are live remote mutations and must honor destructive-operation safeguards.

Test signals: no direct command tests in this subset. Generic Oracle integration tests do not necessarily cover backend commands, multipart cleanup, or archive restore behavior.
