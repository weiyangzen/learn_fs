<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/NTLMAuthenticationProviderBase.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/NTLMAuthenticationProviderBase.cs

## Purpose
`NTLMAuthenticationProviderBase` adapts raw NTLMSSP messages to the generic `IGSSMechanism` contract.

## Important APIs and Types
It exposes the NTLMSSP OID through `Identifier`. `AcceptSecurityContext()` validates the NTLM signature, reads the message type, and dispatches to abstract `GetChallengeMessage()` or `Authenticate()`. Subclasses must also implement context deletion and context attribute retrieval.

## Control Flow
Type 1 negotiate messages create/replace context and emit a challenge. Type 3 authenticate messages consume the existing context and return the authentication status without an output token. Any invalid signature, unsupported message type, or challenge message sent in the wrong direction returns `SEC_E_INVALID_TOKEN`.

## State, Dependencies, and Integration
The base class itself is stateless. `IndependentNTLMAuthenticationProvider` supplies the actual context and validation logic. `GSSProvider` registers implementations through the `IGSSMechanism` interface.

## Risks and Test Signals
There is no explicit check that authenticate has a non-null context; subclasses must enforce it. Tests should verify type dispatch, invalid signature rejection, challenge-message rejection, identifier equality with `GSSProvider.NTLMSSPIdentifier`, and that output tokens are null on final authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/NTLMAuthenticationProviderBase.cs -->
