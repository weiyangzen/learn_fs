# sources/user-network-fs/smblibrary/SMBLibrary/Server/NameServer.cs

## Purpose

Implements a minimal NetBIOS name service responder and name registration broadcaster for the server's IPv4 address.

## Important APIs, Types, And Functions

Constructor validates IPv4 concrete address and computes broadcast address. `Start` binds UDP port 137 and begins async receive plus registration thread. `Stop` closes the client. `GetBroadcastAddress` computes subnet broadcast address.

## Control Flow

Receive callback parses name-service packets. NB queries for the local machine workstation/file-server suffix receive positive address responses. NBSTAT requests receive workstation, file server, and workgroup names. Registration sends three name registration requests four times to broadcast.

## State And Persistence Behavior

Holds UDP client, server/broadcast addresses, and listening flag. No durable persistence.

## Dependencies And Integration Points

Uses NetBIOS packet classes, `UdpClient`, `Environment.MachineName`, and threading.

## Risks And Edge Cases

Binding directly to port 137 may require privileges and conflict with OS services. `Stop` assumes `m_client` exists. Packet parse exceptions are swallowed. Only IPv4 and a fixed `WORKGROUP` are supported.

## Test Signals

Test broadcast address math, constructor rejection of `IPAddress.Any` and IPv6, NB query responses, NBSTAT responses, stop during receive, and registration send count.

Source-read signal: reviewed the complete local source file for this item.
