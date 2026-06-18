
# sources/user-network-fs/rclone/lib/buildinfo/osversion.go

Purpose: non-Windows OS version/kernel reporting for build info.

Important APIs/types/functions: build tag `!windows`; `GetOSVersion() (osVersion, osKernel string)` uses `gopsutil/host` to collect platform, version, kernel version, and kernel architecture.

Control flow: platform/version form `osVersion`; kernel version forms `osKernel`; kernel arch appends `(64 bit)` to OS version when appropriate and appends architecture to kernel string.

State/persistence: no state.

Dependencies/integration: used by rclone version/build diagnostics; depends on `github.com/shirou/gopsutil/v4/host`.

Risks: all host probes are best-effort and silently omit fields on error. 64-bit detection is string-suffix based.

Test signals: observable in build/version output; no direct tests here.
