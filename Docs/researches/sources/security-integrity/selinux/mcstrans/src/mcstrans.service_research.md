<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.service -->
# sources/security-integrity/selinux/mcstrans/src/mcstrans.service

## Purpose

Systemd unit for running the mcstrans daemon. The source was read completely for this report (15 lines).

## Important APIs, Types, and Functions

Declares service metadata, starts `mcstransd`, supports reload through SIGHUP or service reload command, and participates in normal multi-user/system SELinux service ordering.

## Control Flow

Systemd controls lifecycle: start executes the daemon, reload asks it to reread translation/color state, stop terminates it and allows socket cleanup.

## State and Persistence Behavior

Persistent state is systemd unit installation plus runtime daemon/socket state outside the unit file.

## Dependencies and Integration Points

Integrates `mcstransd` with distributions that use systemd units from the mcstrans build.

## Risks and Edge Cases

Risks are stale executable paths, reload semantics drifting from daemon signal handling, and service ordering that starts before SELinux paths/config are ready.

## Test Signals

Signals are `systemctl start/reload/stop mcstrans`, daemon socket existence, and journal messages.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.service -->
