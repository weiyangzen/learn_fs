<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.service.in -->
# sources/user-network-fs/ksmbd-tools/ksmbd.service.in

## Purpose

Template for a systemd service that starts `ksmbd.mountd`.

## Important APIs, Types, and Functions

Uses substitutions for `@sbindir@` and `@runstatedir@`. The unit declares network ordering, loads the `ksmbd` kernel module before start, runs mountd in foreground mode, and stores `PIDFile=@runstatedir@/ksmbd.lock`.

## Control Flow

systemd starts the service after `network.target`, runs `modprobe ksmbd`, then executes `ksmbd.mountd -n`. Restart is disabled by default.

## State and Persistence Behavior

Runtime state is the mountd lock/pid file under runstatedir and kernel module state.

## Dependencies and Integration Points

Depends on systemd, modprobe, the kernel ksmbd module, generated path substitutions, and the installed `ksmbd.mountd` symlink.

## Risks and Edge Cases

If runstatedir does not match the compiled PATH_LOCK value, service tracking and control commands can fail. Kernel module load failures prevent service startup.

## Test Signals

Install into a staging systemd unit directory and verify `systemd-analyze verify`, correct path substitution, and service start/stop with the kernel module available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.service.in -->
