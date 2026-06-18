<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/IGSSMechanism.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/IGSSMechanism.cs

## Purpose
`IGSSMechanism` defines the small mechanism contract consumed by `GSSProvider`. It abstracts NTLM or future Kerberos-like mechanisms behind GSS-style operations.

## Important APIs and Types
`AcceptSecurityContext(ref object context, byte[] inputToken, out byte[] outputToken)` mirrors `GSS_Accept_sec_context`. `DeleteSecurityContext(ref object context)` releases mechanism state. `GetContextAttribute(object context, GSSAttributeName attributeName)` exposes negotiated identity/session attributes. `Identifier` returns the mechanism OID used in SPNEGO negotiation.

## Control Flow
The interface itself has no implementation, but the expected flow is multi-step: a provider creates or passes an opaque context object, the mechanism consumes one incoming token per call, and the mechanism reports success, continuation, or failure through `NTStatus`.

## State, Dependencies, and Integration
State is deliberately opaque (`object`) so implementations can store NTLM challenge/session data without leaking concrete types. `NTLMAuthenticationProviderBase` is the primary implementation in this subset. `GSSProvider` uses `Identifier` for selection and forwards context lifecycle calls to the selected mechanism.

## Risks and Test Signals
The untyped context makes implementation errors runtime-only. Tests should verify each mechanism tolerates null initial context, rejects out-of-order tokens, returns stable identifiers, clears context on deletion, and exposes attributes consistently after successful authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/IGSSMechanism.cs -->
