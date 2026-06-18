# sources/user-network-fs/rclone/lib/systemd/notify.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/systemd/notify.go -->
## sources/user-network-fs/rclone/lib/systemd/notify.go

Purpose: sends readiness, stopping, and status notifications to systemd.

Important APIs and control flow: `Notify()` sends `SdNotifyReady`, then returns a finalizer function that sends `SdNotifyStopping` exactly once. It also registers that finalizer with `atexit`, and the returned function unregisters it before finalizing. `UpdateStatus(status)` sends `STATUS=<status>` through `daemon.SdNotify`.

State, dependencies, and integration: `Notify` uses a local `sync.Once` and an atexit registration handle. Dependencies are go-systemd `daemon`, rclone `fs` logging, and rclone `lib/atexit`. It integrates with long-running commands under systemd.

Risks and test signals: docs warn `Notify` should generally be called once; multiple calls would create multiple atexit registrations. Errors are logged for ready/stopping but returned only for status updates. No tests in this subset exercise systemd notification behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/systemd/notify.go -->
