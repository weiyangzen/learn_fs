# sources/test-tools/syzkaller/pkg/osutil/osutil_nonlinux.go

Purpose: Non-Linux fallbacks for OS helpers whose Linux implementation depends on statx, namespaces, process groups, or block accounting.

Important APIs: `fileTimes`, `RemoveAll`, `SystemMemorySize`, `prolongPipe`, `Sandbox`, `SandboxChown`, `setPdeathsig`, `killPgroup`, and `sysDiskUsage`.

Control flow and state: Uses modification time for both creation and modification time, delegates removal to `os.RemoveAll`, returns 0 for memory size, no-ops sandbox/PDEATHSIG/pipe behavior, and reports disk usage as file size.

Dependencies and integration: Allows packages using osutil to build and run on non-Linux platforms with reduced semantics.

Risks: Process timeout/cancel on non-Linux cannot kill full process groups via `killPgroup`. Disk usage is logical size rather than allocated blocks. Sandbox calls silently do nothing.

Test signals: Many osutil tests skip Linux-specific disk usage on non-Linux; no direct non-Linux behavior tests in this shard.
