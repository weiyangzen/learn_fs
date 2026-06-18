<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/debug.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/debug.go

Purpose: command-line debug flag integration for FUSE tests.

Important APIs, types, and functions: defines `flagDebug`, global `debug`, `Set`, `String`, `IsBoolFlag`, `logMsg`, `DebugByDefault`, and registers `-fuse.debug` in init.

Control flow: setting the flag true assigns `fuse.Debug = logMsg`; setting false restores a no-op. `MountedFuncT` later uses `debug` to wire test logging.

State and persistence behavior: process-global flag value and `fuse.Debug` function pointer are mutated.

Dependencies and integration points: integrates Go flags, log package, fuse debug hook, and fstestutil mount helpers.

Risks and test signals: global debug state can leak across tests. Signals are visible FUSE logs when `-fuse.debug` or `DebugByDefault` is active.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/debug.go -->
