# sources/user-network-fs/rclone/cmd/mountlib/check_other.go

Purpose: non-Linux fallback for mount emptiness/readiness checks.

Important APIs: `CheckMountEmpty`, `CheckMountReady`, and `CanCheckMountReady = false`. `CheckMountEmpty` delegates to generic directory listing; `CheckMountReady` is a no-op because reliable mount readiness detection is unavailable.

Control flow/state: no persistent state; readiness wait on these platforms relies on fixed daemon wait timing rather than probing. Dependencies are minimal.

Risks: daemonized mounts can report readiness only by elapsed wait, so slow mounts may still not be ready and failed mounts may be detected only by daemon process death. Coverage is platform/integration dependent.
