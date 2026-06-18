# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/org.ganesha.nfsd.conf

## Purpose

This DBus policy file controls access to the `org.ganesha.nfsd` service on the system bus.

## Important APIs, Types, and Functions

The policy grants user `root` permission to own `org.ganesha.nfsd`, send to that destination, and send to selected interfaces: `org.freedesktop.DBus.Introspectable`, `org.ganesha.nfsd.CBSIM`, and `org.ganesha.nfsd.admin`.

## Control Flow

DBus daemon reads this XML policy at service/policy load time. There is no executable code.

## State and Persistence Behavior

Installed policy persistently affects system bus authorization. It does not maintain runtime state itself.

## Dependencies and Integration Points

It depends on DBus busconfig format and is installed under a DBus system policy directory by packaging/build scripts. It directly impacts whether the Python administration scripts can reach Ganesha interfaces.

## Risks and Edge Cases

The policy shown allows only root. Tools run by non-root users will fail unless additional distro policy exists. It mentions admin and CBSIM but not every interface used by newer tools, so effective access may depend on broader destination send permission or other policy files.

## Test Signals

System integration tests should verify root can own and call the service and non-root behavior matches expected security policy. DBus policy validation can parse the XML against the busconfig DTD.
