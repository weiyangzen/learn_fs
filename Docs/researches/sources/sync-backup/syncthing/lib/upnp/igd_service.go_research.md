# sources/sync-backup/syncthing/lib/upnp/igd_service.go

Purpose: represents a discovered UPnP IGD control service and implements NAT device operations for IPv4 port mapping and IPv6 pinholes.

Important APIs and control flow: `IGDService` records UUID, device, service ID, control URL, URN, local IPv4, and network interface. `AddPinhole` enumerates interface addresses, handles explicit listener IPs, skips IPv4/private/non-GUA addresses, and attempts WANIPv6FirewallControl pinholes for global IPv6 addresses. `tryAddPinholeForIP6` maps TCP/UDP to protocol numbers, sends SOAP with the internal IPv6 as local source, parses UPnP faults or logs returned unique ID. `AddPortMapping` requires `LocalIPv4`, sends SOAP `AddPortMapping`, and retries with permanent lease on UPnP error 725. `DeletePortMapping` sends SOAP delete. `GetExternalIPv4Address` parses SOAP response. `SupportsIPVersion` distinguishes IPv6 firewall service from IPv4 services. `ID` builds a unique diagnostic identifier.

State and persistence: no persisted state; remote router state changes via SOAP leases/pinholes.

Dependencies and integration: implements `nat.Device` expectations; depends on `netutil`, `nat`, SOAP helpers in `upnp.go`.

Risks: router SOAP behavior varies; partial IPv6 pinhole success is accepted. XML body fields interpolate description/IP data without escaping. Tests cover SOAP parsing indirectly in `upnp_test.go`.
