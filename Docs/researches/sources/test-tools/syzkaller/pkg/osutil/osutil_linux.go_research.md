# sources/test-tools/syzkaller/pkg/osutil/osutil_linux.go

Purpose: Linux-specific implementations for file timestamps, robust recursive removal, memory size, command sandboxing, parent-death/process-group handling, pipe sizing, and disk usage.

Important APIs: `fileTimes`, `RemoveAll`, `SystemMemorySize`, `Sandbox`, `SandboxChown`, plus internal `removeImmutable`, `initSandbox`, `usernameToID`, `setPdeathsig`, `killPgroup`, `prolongPipe`, and `sysDiskUsage`.

Control flow: `fileTimes` uses `statx` for birth and mtime. `RemoveAll` recursively attempts to unmount children, removes the tree, and retries after clearing immutable/append flags. `Sandbox` lazily resolves the `syzkaller` user unless not root, CI, or disabled by env; it can set new namespaces and/or credentials on an exec command. Command helpers set `Pdeathsig` and process group. `prolongPipe` tries increasing pipe sizes. Disk usage uses allocated blocks and handles inline/small file cases.

State and persistence: Uses package-level sandbox cache guarded by `sync.Once`. Mutates command `SysProcAttr`, file ownership, mount state, and filesystem flags.

Dependencies and integration: Supports `osutil.Run`, manager process spawning, cleanup, VM preparation, and disk accounting.

Risks: Sandbox requires a `syzkaller` user when enabled. `killPgroup` assumes process started and process group exists. `RemoveAll` ignores errors from recursive child removals/unmount attempts until final removal. Disk usage uses Linux stat details and can vary by filesystem.

Test signals: `TestDiskUsage` covers Linux usage accounting; command/sandbox behavior is not directly tested here.
