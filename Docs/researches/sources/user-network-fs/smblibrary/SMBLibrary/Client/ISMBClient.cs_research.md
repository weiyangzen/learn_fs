<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBClient.cs

## Purpose
`ISMBClient` defines the high-level SMB client contract for connecting, authenticating, listing shares, tree connecting, echoing, and exposing negotiated transfer sizes.

## Important APIs and Types
Methods include address/name `Connect`, `Disconnect`, two `Login` overloads, `Logoff`, `ListShares`, `TreeConnect`, and `Echo`. Properties expose `MaxReadSize`, `MaxWriteSize`, and `IsConnected`.

## Control Flow
The interface prescribes a lifecycle: connect transport, login, optionally list shares or tree connect, use file stores, logoff, disconnect.

## State, Dependencies, and Integration
Implementations such as `SMB1Client` hold transport/session state and return `ISMBFileStore` instances for share operations. Higher-level code can target this interface without caring about SMB dialect-specific classes.

## Risks and Test Signals
The interface does not expose dialect, signing, encryption, DFS, or cancellation semantics. Tests for implementations should verify lifecycle preconditions, status returns, max-size values after negotiation, and consistent disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBClient.cs -->
