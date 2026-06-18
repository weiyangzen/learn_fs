# Research: sources/object-store/minio-mc/cmd/mv-main.go

## sources/object-store/minio-mc/cmd/mv-main.go

Purpose: implements `mc mv` by reusing copy-session behavior and deleting successfully moved sources through a shared remove manager.

Important APIs and types: `mvCmd` declares flags; `removeClientInfo` and `removeManager` multiplex remove operations by target alias; `readErrors`, `add`, and `close` manage remove streams; `mainMove` is the command entrypoint; `rmManager` is the package-global manager.

Control flow: `mainMove` validates copy syntax, rejects moving a source into its destination prefix for two-argument cases, parses encryption keys, calls `doCopySession(..., true)` to perform move-mode copies, then closes `rmManager` so queued source deletions complete. `removeManager.add` lazily creates one `Client.Remove` stream per alias and sends `ClientContent` entries into a buffered channel.

State and persistence: mutates destination objects through copy-session code and deletes source objects/files through `Client.Remove`. `rmManager` persists as package global state across invocations.

Dependencies and integration: relies heavily on copy command helpers outside this subset, shared `Client.Remove`, `RemoveResult`, `URLs`, context cancellation, and global copy status/output handling.

Risks and tests: the global `rmManager` can retain closed channels or client info across repeated in-process command calls, which is a test/embedding risk. Error handling in remove goroutines prints but does not directly fail `mainMove`. No direct tests are present.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mv-main.go -->
