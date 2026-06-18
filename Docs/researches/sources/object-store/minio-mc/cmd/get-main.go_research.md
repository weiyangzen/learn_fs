# sources/object-store/minio-mc/cmd/get-main.go

Purpose: Implements `mc get`, a restricted S3-object-to-local download command.

Important APIs/types/functions: `getFlags`, `getCmd`, `mainGet`, and `printGetURLsError`.

Control flow: Requires `SOURCE TARGET`, parses encryption keys, prepares get URLs through `prepareGetURLs`, then calls shared `doCopy` for each result with progress accounting. It reports URL preparation/download errors and final progress.

State and persistence: Downloads remote S3 object data to local filesystem target.

Dependencies/integration: Reuses copy transfer machinery, encryption parsing, progress bar/accounter, and global context.

Risks: Only one source is supported by get URL type guessing. Some total byte progress is not accumulated in `mainGet` before calling `doCopy`, relying on transfer update behavior.

Test signals: No direct tests.
