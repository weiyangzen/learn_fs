<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ConnectionState.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/ConnectionState.cs

## Purpose
`ConnectionState` groups a connected socket with its NetBIOS-over-TCP receive buffer for asynchronous SMB1 client I/O.

## Important APIs and Types
The constructor stores a `Socket` and creates an `NBTConnectionReceiveBuffer`. Read-only `ClientSocket` and `ReceiveBuffer` properties expose them to callback code.

## Control Flow
There is no behavior beyond construction and property access. `SMB1Client.ConnectSocket()` creates this state and passes it to `BeginReceive`; callbacks lock and mutate the receive buffer.

## State, Dependencies, and Integration
State is per TCP connection. It depends on `System.Net.Sockets` and `SMBLibrary.NetBios`. Disposal is managed by `SMB1Client`, not by this container.

## Risks and Test Signals
The class does not own cleanup semantics, so callback paths must dispose the receive buffer consistently. Tests are mostly integration-level: socket disconnect, receive buffer disposal on errors, and no reuse of disposed state after reconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ConnectionState.cs -->
