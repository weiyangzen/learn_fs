# sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go -->
## sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go

Purpose: wraps `github.com/coreos/go-systemd/v22/activation` for non-Windows, non-Plan-9 platforms.

Important APIs and control flow: `ListenersWithNames()` delegates directly to `activation.ListenersWithNames()`. `Listeners()` delegates to `activation.Listeners()`.

State, dependencies, and integration: there is no local state. It depends on `net` for signatures and go-systemd activation for behavior. It integrates with server commands that can be launched through systemd socket activation.

Risks and test signals: all semantics and environment parsing are inherited from go-systemd. The wrapper exists primarily for platform compatibility. No tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go -->
