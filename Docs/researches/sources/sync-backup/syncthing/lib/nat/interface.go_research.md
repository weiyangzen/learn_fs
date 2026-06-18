## sources/sync-backup/syncthing/lib/nat/interface.go

Purpose: declares the common NAT/firewall traversal abstraction used by NAT providers such as NAT-PMP and UPnP.

Important APIs: `Protocol` constants `TCP` and `UDP`; `IPVersion` constants `IPvAny`, `IPv4Only`, and `IPv6Only`; `Device` interface with ID, local IPv4 gateway address, port mapping, IPv6 pinhole, external IPv4 address, and IP-version support methods.

Control flow and state: pure type definitions.

Dependencies and integration points: `nat.Service` consumes `Device` implementations from registered discoverers. `pmp.wrapper` implements this interface for NAT-PMP. Other packages create `Mapping` values with protocol and IP version constraints.

Risks: the interface mixes IPv4 mapping and IPv6 pinhole capabilities; implementations must return accurate `SupportsIPVersion` values or the service can attempt unsupported operations.

Test signals: exercised indirectly by NAT service and PMP integration; no direct interface tests.
