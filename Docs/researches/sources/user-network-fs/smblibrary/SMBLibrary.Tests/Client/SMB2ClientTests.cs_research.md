<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/Client/SMB2ClientTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/Client/SMB2ClientTests.cs

## Purpose
`SMB2ClientTests.cs` verifies that `SMB2Client.Connect` fails quickly when a TCP peer either never sends an SMB response or sends invalid non-SMB data.

## Important APIs, Types, And Functions
The MSTest class owns a loopback `TcpListener`, randomized port, `m_clientConnected`, and callbacks `AcceptTcpClient_DoNotReply` and `AcceptTcpClient_SendNonSmbData`. Tests instantiate `SMB2Client(timeoutInMilliseconds)` and call `Connect(IPAddress.Loopback, SMBTransportType.DirectTCPTransport, port)`.

## Control Flow
`TestInitialize` starts a loopback listener. Each test begins an async accept callback, starts `client.Connect` on a thread while a stopwatch runs, waits until the listener accepted the connection, then asserts `Connect` returned false and elapsed time is under 200 ms despite the nominal 1000 ms timeout.

## State And Persistence
State is transient network listener/client state and thread-local flags. No files are written.

## Dependencies And Integration Points
The tests depend on `SMBLibrary.Client.SMB2Client`, direct TCP transport, .NET `TcpListener`, and loopback networking. They protect connection negotiation failure paths in client code.

## Risks
The assertions are timing-sensitive and can be flaky on slow or heavily loaded systems. The tests do not close accepted `TcpClient` instances or the listener in a cleanup method. Random port selection may still collide. The declared `ManualResetEvent` variables are unused.

## Test Signals
They signal that malformed or silent servers should not make the client block for the full timeout once the TCP connection is established. They do not validate successful negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/Client/SMB2ClientTests.cs -->
