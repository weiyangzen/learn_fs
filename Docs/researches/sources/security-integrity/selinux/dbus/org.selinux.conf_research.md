# sources/security-integrity/selinux/dbus/org.selinux.conf

## Purpose

This D-Bus system bus configuration controls ownership and message routing for the `org.selinux` service.

## Policy Behavior

Only `root` may own the `org.selinux` bus name. The default context allows clients to send messages to `org.selinux`; method-level authorization is delegated to PolicyKit checks in `selinux_server.py`.

## State And Persistence

Installed under `/etc/dbus-1/system.d/`, this file persists bus policy for the system D-Bus daemon. It does not define methods or authorization semantics itself.

## Dependencies And Integration Points

It depends on D-Bus busconfig DTD semantics. It integrates with `org.selinux.service`, which starts the root service, and `org.selinux.policy`, which defines the PolicyKit action defaults.

## Risks

The broad default `allow send_destination="org.selinux"` is intentional but places all authorization responsibility on the service implementation. Any unauthenticated method in `selinux_server.py` would be reachable by any bus client.

## Test Signals

Bus policy tests should confirm non-root users cannot own `org.selinux`, ordinary clients can call into the service, and unauthorized method calls are denied by PolicyKit rather than by bus routing.
