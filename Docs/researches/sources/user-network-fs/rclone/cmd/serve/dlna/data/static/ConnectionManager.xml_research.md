# sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ConnectionManager.xml

## Purpose

This SCPD document declares the UPnP ConnectionManager service contract exposed by the DLNA server.

## Important APIs, Types, and Functions

The XML declares actions `GetProtocolInfo`, `PrepareForConnection`, `ConnectionComplete`, `GetCurrentConnectionIDs`, and `GetCurrentConnectionInfo`, plus state variables for source/sink protocol info, connection IDs, direction, status, and related argument types.

## Control Flow

Clients discover this file from the root descriptor, then invoke SOAP actions at the server control URL. The Go implementation currently handles only `GetProtocolInfo`.

## State and Persistence Behavior

This is static metadata with no runtime persistence.

## Dependencies and Integration Points

It is embedded into `data.Assets` and served under `/static/`. Handler response argument names and order must match the XML.

## Risks and Test Signals

The XML advertises more actions than the Go service implements, so clients calling the optional actions receive invalid action errors. Root descriptor tests confirm the service is linked, but there are no schema or full action coverage tests.
