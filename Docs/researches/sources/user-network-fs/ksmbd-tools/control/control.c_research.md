<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/control.c -->
# sources/user-network-fs/ksmbd-tools/control/control.c

## Purpose

Implements `ksmbd.control`, an administrative CLI for shutting down, reloading, listing shares, toggling kernel debug components, and printing the kernel module version.

## Important APIs, Types, and Functions

Important functions are `control_main`, `control_shutdown`, `control_reload`, `control_list`, `control_show_version`, and `control_debug`. It uses `/sys/class/ksmbd-control/kill_server`, `/sys/class/ksmbd-control/debug`, `/sys/module/ksmbd/version`, `PATH_FIFO`, and `PATH_LOCK`.

## Control Flow

The CLI dispatches immediately on the first action option. Shutdown SIGTERMs mountd via the parsed lock and writes `hard` to the kernel control attribute. Reload sends SIGHUP. List creates a per-client FIFO, asks mountd with SIGUSR1, blocks for SIGIO, and splices FIFO data to stdout. Debug writes a component string then reads back active components.

## State and Persistence Behavior

Runtime state includes sysfs control attributes, the mountd lock file, and transient `ksmbd.fifo.<pid>` FIFOs. No config files are modified.

## Dependencies and Integration Points

Depends on config_parser lock parsing, tools logging/version helpers, pthread signal masks, fcntl async I/O, sysfs ksmbd control, and mountd's SIGUSR1 list protocol.

## Risks and Edge Cases

Sysfs files may not support lseek on all kernels; version/debug paths assume seekable attributes. The FIFO protocol depends on signal delivery and cleanup on interrupt. Action options are mutually exclusive by first match rather than validation.

## Test Signals

Tests include help/version without kernel support, reload with fake lock, FIFO list integration with mountd, shutdown/debug/version on a system with the kernel module, and cleanup of FIFOs on failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/control.c -->
