<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenResponse.cs

## Purpose
`SimpleProtectedNegotiationTokenResponse` implements RFC 4178 `negTokenResp` for SPNEGO acceptor/initiator continuation and completion messages.

## Important APIs and Types
`NegState` models accept-completed, accept-incomplete, reject, and request-mic. Token fields are `NegState`, `SupportedMechanism`, `ResponseToken`, and `MechanismListMIC`; constants define their context-specific tags.

## Control Flow
The parser reads the construction and inner sequence, then loops over optional fields. `NegState` is a DER enum wrapped by tag `0xA0`; supported mechanism is an OID; response token and MIC are octet strings. `GetBytes()` computes nested field sizes and emits optional fields in protocol order.

## State, Dependencies, and Integration
Instances are mutable SPNEGO DTOs. `GSSProvider` creates response tokens from mechanism output and maps `NTStatus.STATUS_SUCCESS` to `AcceptCompleted`, `SEC_I_CONTINUE_NEEDED` to `AcceptIncomplete`, and other statuses to `Reject`. `NTLMAuthenticationClient` reads server response tokens and emits final NTLM authenticate tokens with a mech-list MIC.

## Risks and Test Signals
Parsing is strict about tags but not about declared/consumed length equality. The code supports RequestMic structurally but provider logic does not enforce MIC negotiation policy. Tests should verify status mapping, bare response parsing, MIC preservation, and malformed optional fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenResponse.cs -->
