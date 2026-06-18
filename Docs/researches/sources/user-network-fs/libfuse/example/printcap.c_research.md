# sources/user-network-fs/libfuse/example/printcap.c

## Purpose
`printcap.c` is a minimal low-level filesystem that mounts a temporary FUSE session only long enough to print the negotiated protocol version and supported kernel/library capability flags, then exits.

## Important APIs, Types, and Functions
The `capabilities[]` table maps `FUSE_CAP_*` bit flags to names, including newer flags such as passthrough, io_uring, idmap, and security context. `print_capabilities()` calls `fuse_get_feature_flag()` for each entry. `pc_init()` prints protocol version and capabilities, then calls `fuse_session_exit(se)`. `pc_oper` only registers `.init`.

## Control Flow
`main()` creates a temporary directory under `/tmp`, prints libfuse version information, creates a low-level session, installs signal handlers, mounts at the temp directory, and enters `fuse_session_loop`. The init callback runs during session initialization, prints capability information, asks the session to exit, and the normal cleanup path unmounts, removes signal handlers, destroys the session, removes the temp directory, and frees args.

## State and Persistence
The only global mutable state is `struct fuse_session *se`. The temporary mountpoint directory exists only for the process duration and is removed before exit. There is no filesystem content beyond initialization.

## Dependencies and Integration Points
The program depends on low-level libfuse and the kernel FUSE protocol. It integrates with the feature negotiation helpers rather than reading `conn->capable` directly. The hardcoded capability table must be updated as new `FUSE_CAP_*` flags are added.

## Risks
The global session pointer must be assigned before init runs; current control flow satisfies that. If mount or cleanup fails, `rmdir` may leave the temporary directory. The table can silently omit newer capabilities, so the program is only as complete as the maintained list.

## Test Signals
Running the binary should print the libfuse version, low-level version, protocol version, and one line per supported capability, then exit successfully. Failure to create/mount the temporary directory should produce a nonzero exit.
