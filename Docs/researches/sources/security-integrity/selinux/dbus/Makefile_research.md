# sources/security-integrity/selinux/dbus/Makefile

## Purpose

This Makefile installs the SELinux D-Bus service files, PolicyKit action metadata, and the Python service implementation.

## Targets And Flow

`all` and `clean` are no-ops. `install` creates D-Bus system configuration, system service, polkit action, and `system-config-selinux` share directories under `DESTDIR` and `PREFIX`, then installs `org.selinux.conf`, `org.selinux.service`, `org.selinux.policy`, and executable `selinux_server.py`. `relabel` and `test` are empty placeholders.

## State And Persistence

The target persists system configuration under `/etc/dbus-1/system.d`, service activation metadata under `$(PREFIX)/share/dbus-1/system-services`, polkit actions under `$(PREFIX)/share/polkit-1/actions`, and the server script under `$(PREFIX)/share/system-config-selinux`.

## Dependencies And Integration Points

It depends on `mkdir`, `install`, `DESTDIR`, and `PREFIX`. Installed files integrate the root-owned `org.selinux` D-Bus name with PolicyKit authorization and D-Bus activation.

## Risks

The install command uses leading `-` for `mkdir` commands, allowing directory creation failures to be ignored. There is no uninstall target or validation that the service script path matches the service file. The server is installed mode `755`, appropriate for execution but important because D-Bus starts it as root.

## Test Signals

Packaging tests should verify the four installed paths, file modes, D-Bus activation of `org.selinux`, and that the PolicyKit actions referenced by `selinux_server.py` are present.
