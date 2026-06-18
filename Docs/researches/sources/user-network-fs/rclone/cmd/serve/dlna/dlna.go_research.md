# sources/user-network-fs/rclone/cmd/serve/dlna/dlna.go

## Purpose

`dlna.go` wires rclone's `serve dlna` command, RC entrypoint, HTTP routes, SOAP dispatch, media resource serving, and SSDP discovery.

## Important APIs, Types, and Functions

Public configuration is `OptionsInfo`, `Options`, global `Opt`, and Cobra `Command`. Core server APIs are `newServer`, `Serve`, `Shutdown`, `Addr`, `rootDescHandler`, `serviceControlHandler`, `soapActionResponse`, `resourceHandler`, `startSSDP`, `ssdpInterface`, and `serveHTTP`. `UPnPService` abstracts individual SOAP services.

## Control Flow

Command/RC code builds VFS and options, `newServer` resolves friendly name and network interfaces, registers ContentDirectory, ConnectionManager, and MediaReceiverRegistrar, builds HTTP routes, binds a listener, and returns a server. `Serve` starts SSDP and HTTP in goroutines, then waits for shutdown. SOAP requests parse the `SOAPACTION` header and envelope body, dispatch to the service map, and return either ordered response XML or a UPnP fault.

## State and Persistence Behavior

Server state is in memory: listener, VFS, selected interfaces, UUID derived from friendly name, wait channel, route handler, and service map. There is no content index persistence; media listing is live VFS access.

## Dependencies and Integration Points

It integrates Cobra, `serve.Command`, RC, rclone VFS, systemd notification, anacrolix UPnP/SOAP/SSDP, embedded data assets, and HTTP clients/players.

## Risks and Test Signals

Risks include SSDP interface filtering, IPv4/IPv6 advertise mismatches, type assertion of resource nodes to `*vfs.File`, goroutine shutdown races if `Shutdown` is called multiple times, and SOAP/XML compatibility. Tests cover root descriptor, media serving, browse requests, receiver registration, RC creation, and content resource URLs.
