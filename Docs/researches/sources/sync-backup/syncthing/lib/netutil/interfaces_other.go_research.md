## sources/sync-backup/syncthing/lib/netutil/interfaces_other.go

Purpose: non-Android network interface enumeration using the standard library.

Important APIs: `Interfaces` calls `net.Interfaces`; `InterfaceAddrsByInterface` calls `intf.Addrs`.

Control flow and state: stateless wrappers under `!android` build constraint.

Dependencies and integration points: used by network utility code and NAT gateway matching on all non-Android platforms.

Risks: standard library interface enumeration can return platform-specific errors or omit down/permission-limited interfaces; callers filter as needed.

Test signals: indirectly exercised by osutil network tests, not directly here.
