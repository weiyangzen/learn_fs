<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/winbindd.c -->
# sources/user-network-fs/samba/source4/winbind/winbindd.c

## Purpose

This file registers a Samba4 server service that runs the Samba3 `winbindd` daemon as a managed child process inside the Samba4 task framework.

## Important APIs, Types, and Functions

- `winbindd_done()` handles child process completion from `samba_runcmd_recv()` and terminates the service task.
- `winbindd_task_init()` constructs the `winbindd` command line and starts it with `samba_runcmd_send()`.
- `server_service_winbindd_init()` registers service names `winbindd` and `winbind`.

## Control Flow

At service initialization, Samba registers `winbindd`/`winbind` with service details that inhibit fork-on-accept and prefork. When the task starts, it sets the process title, builds the path `${dyn_SBINDIR}/winbindd`, adds a `--configfile` option only for non-default config paths, then runs winbindd with `-D`, `--foreground`, and `server role check:inhibit=yes`. A callback is attached so any normal or abnormal child exit terminates the parent task.

## State and Persistence Behavior

This file creates a child process and supervises its lifetime. It does not directly write databases or files, but child winbindd will use Samba runtime directories, winbind caches, and configuration. The parent service terminates when the child exits.

## Dependencies and Integration Points

It depends on Samba service/task registration, process model details, `UTIL_RUNCMD`, dynconfig paths, debug output settings, and winbind client headers. The Waf build registers it as `service_winbindd` in the `service` subsystem.

## Risks and Edge Cases

If `dyn_SBINDIR/winbindd` is missing or fails quickly, the service terminates. `winbindd_done()` logs `sys_errno` as an exit status, which may be imprecise depending on `samba_runcmd_recv()` semantics. Empty `config_file` is still passed as an argument position, relying on runcmd handling.

## Test Signals

Pass signals are successful service registration under both names, child winbindd startup, continued foreground operation, and task termination when the child exits or fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/winbindd.c -->
