## sources/sync-backup/syncthing/lib/pmp/pmp.go

Purpose: NAT-PMP discovery provider and adapter implementing the `nat.Device` interface.

Important APIs: package `init` registers `Discover` with `nat.Register`. `Discover(ctx, renewal, timeout)` finds the default gateway, creates a NAT-PMP client, queries external address under timeout, and returns a `wrapper` device. `wrapper` implements `ID`, `GetLocalIPv4Address`, `AddPortMapping`, `AddPinhole`, `SupportsIPVersion`, and `GetExternalIPv4Address`.

Control flow and state: discovery calls `netutil.Gateway` through `svcutil.CallWithContext`, logs and returns nil on failure, then calls NAT-PMP external address to validate the gateway. The wrapper ID includes `NAT-PMP@<gateway>`. `AddPortMapping` maps Syncthing `nat.Protocol` to lowercase NAT-PMP protocol strings, converts lease duration to seconds, and returns the mapped external port. IPv6 pinholes are unsupported and return an error; `SupportsIPVersion` accepts `IPvAny` and `IPv4Only`.

Dependencies and integration points: depends on `jackpal/go-nat-pmp`, `nat`, `netutil.Gateway`, `osutil.TCPPing` or local address helpers as visible in wrapper behavior, and the NAT service registry.

Risks: gateway discovery and external address calls can fail under router/firewall/Android restrictions. NAT-PMP supports IPv4 only. Lease duration conversion truncates to seconds. The package has only placeholder tests.

Test signals: no substantive tests; behavior is covered only through integration/manual NAT environments.
