<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_lib.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_lib.c

## Purpose
Provides `nfs_libmain()`, an embedded/library startup path for Ganesha without standalone CLI parsing, pidfile locking, daemonization, or full signal handling.

## Important APIs, Types, And Functions
- `nfs_libmain()` initializes and starts the service.
- `my_nfs_start_info` defaults `drop_caps` to false.
- `export_cleanup()` and `export_cleanup_element` clean `export_opt_lock`.

## Control Flow
The function sets boot time, adopts optional config/log paths, resolves hostname, initializes prereqs/logging and `nfs_init`, blocks `SIGPIPE`, initializes URL/config parsing, applies log config, starts FSALs, loads parameters, initializes packages, reads data servers, initializes recovery/netconfig/grace, initializes export locking, reads exports, reports config errors, frees parse tree, and calls `nfs_start()`.

## State And Persistence Behavior
Mutates standard daemon globals and registers cleanup for export option locking. It frees library-owned strings after service exit.

## Dependencies And Integration Points
Shares initialization helpers with standalone startup: config, logging, FSAL, parameters, server packages, data servers, recovery, netconfig, grace, exports, and service start.

## Risks
- Blocks only `SIGPIPE`, unlike standalone startup.
- No pidfile locking, daemonization, dynamic metrics startup, `PR_SET_IO_FLUSHER`, or fatal warning option.
- `nfs_libmain()` blocks until admin shutdown.
- Globals overlap with `nfs_main.c` entry path.

## Test Signals
Test embedded startup, parse failures, no exports, recovery failure, `SIGPIPE`, `admin_halt()` shutdown, cleanup callback, and parity with standalone shared subsystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_lib.c -->
