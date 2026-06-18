# sources/user-network-fs/blobfuse2/cmd/unmount_all.go
## sources/user-network-fs/blobfuse2/cmd/unmount_all.go

Purpose: implements `blobfuse2 unmount all`, which enumerates all blobfuse2 mounts and attempts to unmount each one.

Important APIs/functions: global `umntAllCmd` with its `RunE`, using `common.ListMountPoints`, `unmountBlobfuse2`, and the inherited `lazy` flag from `unmountCmd`.

Control flow: the command reads the lazy flag, lists mount points, and initializes counters plus an aggregate error message. It increments `mountfound` for each mount, calls `unmountBlobfuse2`, increments `unmounted` on success, and appends per-mount error details on failure. If no mounts are found it prints `Nothing to unmount`; otherwise it prints a success count. Any partial failure returns a combined error.

State and persistence: changes OS mount state and emits stdout. No local files are written.

Dependencies/integration: Linux mount-table parsing through `common.ListMountPoints`, the unmount helper in `unmount.go`, Cobra subcommand registration, and process-level fusermount commands.

Risks: a failure on one mount does not stop attempts for later mounts, which is good operationally, but errors are plain string aggregation without structured detail. Behavior depends on `common.ListMountPoints` only returning lines prefixed by `blobfuse2`. The command assumes inherited flag lookup succeeds.

Test signals: direct coverage is mostly through `util_test.go` calling `../blobfuse2 unmount all` and `unmount_test.go` covering inherited lazy behavior through the parent command.
