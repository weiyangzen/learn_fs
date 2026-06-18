<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/IntegrationTests/LoginTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/IntegrationTests/LoginTests.cs

## Purpose
`LoginTests.cs` is an in-process SMB2 client/server integration test for NTLM login success, reconnect/login behavior, and failed credentials.

## Important APIs, Types, And Functions
The class creates an `SMBServer` with an empty `SMBShareCollection`, an `IndependentNTLMAuthenticationProvider` that accepts password `"password"`, and a `GSSProvider`. Tests use `SMB2Client.Connect`, `Login`, `Logoff`, and `Disconnect`.

## Control Flow
`TestInitialize` selects a randomized loopback port, builds the server with NTLM GSS authentication, and starts it. `TestCleanup` stops the server. Tests connect a client, then assert success for valid credentials, success after logoff/disconnect/reconnect, and `STATUS_LOGON_FAILURE` for wrong-case password.

## State And Persistence
State is transient process-local server, client sessions, and TCP listeners. No shares are mounted and no files are persisted.

## Dependencies And Integration Points
The tests integrate SMB server startup, GSS/SPNEGO or NTLM negotiation, SMB2 client session setup, logoff, reconnect, and independent NTLM provider behavior.

## Risks
Random port selection may collide. The tests assume loopback networking and thread scheduling are reliable. They do not validate tree connect, guest/anonymous login, signing, encryption, or real OS credential providers.

## Test Signals
Good end-to-end signal for basic SMB2 authentication lifecycle using the independent NTLM provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/IntegrationTests/LoginTests.cs -->
