<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationToken.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationToken.cs

## Purpose
`SimpleProtectedNegotiationToken` is the abstract base for SPNEGO tokens. It adds/removes the generic GSS-API application header and dispatches encoded token bodies to init, init2, or response classes.

## Important APIs and Types
`ApplicationTag` is `0x60`, and `SPNEGOIdentifier` is the SPNEGO OID. `GetBytes()` is implemented by concrete token classes. `GetBytes(bool includeHeader)` optionally prepends the RFC 2743 mechanism-independent token header. `ReadToken()` parses a token from bytes and returns `SimpleProtectedNegotiationTokenInit`, `SimpleProtectedNegotiationTokenInit2`, `SimpleProtectedNegotiationTokenResponse`, or null.

## Control Flow
When the first tag is the application tag, the parser reads total length, validates the object identifier tag and SPNEGO OID, then dispatches on the next context-specific token tag. A server-initiated init token is interpreted as `NegTokenInit2`; normal client init is interpreted as `NegTokenInit`. Bare `negTokenResp` without a GSS header is also accepted.

## State, Dependencies, and Integration
The class is stateless. It integrates `DerEncodingHelper`, `ByteReader`, `ByteWriter`, and `ByteUtils` with `GSSProvider` and `NTLMAuthenticationClient`.

## Risks and Test Signals
`ReadToken()` returns null for structural mismatches but can throw for truncated input. It does not verify that consumed bytes match declared total length. Tests should cover header/no-header response parsing, SPNEGO OID mismatch, server-initiated init2 dispatch, and malformed lengths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationToken.cs -->
