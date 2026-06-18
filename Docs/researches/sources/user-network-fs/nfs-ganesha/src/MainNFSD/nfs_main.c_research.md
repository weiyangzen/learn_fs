<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_main.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_main.c

## Purpose
Standalone daemon entry point. It parses CLI options, initializes logging/memory, optionally daemonizes, locks/writes the pidfile, parses configuration, starts FSALs and packages, initializes monitoring/recovery/grace/exports, and calls `nfs_start()`.

## Important APIs, Types, And Functions
- `main()` is the executable entry.
- `main_strdup()` allocates early strings.
- `valid_stack_size()` validates `-S`.
- `load_lttng()` loads trace libraries when enabled.
- CLI options cover version, log/debug/config/pid paths, foreground, stack size, default config dump, epoch, node ID/VIP, crash trace, fatal config errors, and LTTng.

## Control Flow
Signals are blocked before logging can spawn threads. The program parses options, initializes prereqs and `nfs_init`, daemonizes if requested, ignores `SIGXFSZ`, opens/locks/fsyncs the pid file, initializes URL/config parsing, applies log config, starts FSALs, loads parameters, applies Linux `PR_SET_IO_FLUSHER`, starts monitoring when enabled, initializes server packages, reads data servers, initializes recovery/netconfig/grace/exports, reports config errors, frees the parse tree, and enters `nfs_start()`.

## State And Persistence Behavior
Persistent effects include daemonization, pidfile locking/content, monitoring listener startup, recovery backend setup, grace/export state, and global runtime config.

## Dependencies And Integration Points
Coordinates CLI, logging, config parsing, FSAL loading, parameter loading, Linux process controls, monitoring, server packages, recovery, netconfig, grace, exports, and lifecycle in `nfs_init.c`.

## Risks
- Signal mask ordering is critical.
- Pidfile locking depends on filesystem semantics.
- Deprecated `-R` exits immediately.
- LTTng/ASAN and `PR_SET_IO_FLUSHER` are platform sensitive.
- `-x` changes whether config warnings are fatal.

## Test Signals
Test all CLI flags, invalid values, foreground/background modes, pid lock contention, config failures/warnings, monitoring fallback, LTTng failure, and signal behavior after startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_main.c -->
