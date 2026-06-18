<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/SocketUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Utilities/SocketUtils.cs

## Purpose
Socket utility helpers for TCP keepalive configuration and forceful socket release across .NET Framework and newer runtimes.

## APIs, Types, and Functions
`SetKeepAlive(Socket, TimeSpan)` delegates to `SetKeepAlive(Socket, bool, TimeSpan, TimeSpan)`. `ReleaseSocket(Socket)` shuts down, disconnects, and closes sockets. Conditional `IsDotNetFramework()` selects runtime-specific keepalive APIs.

## Control Flow, State, and Persistence
Keepalive always enables socket keepalive. On .NET Framework it builds a 12-byte `tcp_keepalive` buffer and calls `IOControl(KeepAliveValues)`. On newer runtimes it sets TCP keepalive time, interval, and non-Windows retry count socket options. Release ignores common socket/object-disposed exceptions and closes the socket. No persistence.

## Dependencies and Integration
Used by `SMBServer` accept and stop paths. Depends on `LittleEndianWriter`, `RuntimeInformation`, and socket APIs.

## Risks and Test Signals
Risks include platform-specific socket option numeric constants, retry-count comment/condition mismatch risk, unchecked `IOControl` failures, and forceful close dropping pending data. Test on .NET Framework, .NET Core/5+ Windows, Linux, null sockets, already-closed sockets, and keepalive timing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/SocketUtils.cs -->
