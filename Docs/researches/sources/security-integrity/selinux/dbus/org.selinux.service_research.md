# sources/security-integrity/selinux/dbus/org.selinux.service

## Purpose

This D-Bus service activation file registers the `org.selinux` service.

## Behavior

It names `org.selinux`, executes `/usr/share/system-config-selinux/selinux_server.py`, and requests `User=root`, so D-Bus activation starts the Python server with root privileges.

## State And Persistence

Installed under `share/dbus-1/system-services`, it persists system service activation metadata.

## Dependencies And Integration Points

It must match the installed path from the D-Bus Makefile and the bus name owned by `selinux_server.py`. It also depends on the script having an executable shebang and mode.

## Risks

Because the service runs as root, method authorization and input validation in `selinux_server.py` are critical. A packaging path mismatch would break D-Bus activation.

## Test Signals

Activation tests should call a harmless method such as `semodule_list` or observe D-Bus service startup and confirm the process runs as root and owns `org.selinux`.
