<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit.cs

## Purpose
`SimpleProtectedNegotiationTokenInit` implements RFC 4178 `negTokenInit` serialization and parsing for the SPNEGO initiator token.

## Important APIs and Types
Fields include `MechanismTypeList`, `MechanismToken`, and `MechanismListMIC`. Constants define the `negTokenInit` tag and child tags for mechanism list, required flags, mechanism token, and MIC. Static helpers read/write mechanism lists and expose `GetMechanismTypeListBytes()` for MIC calculation.

## Control Flow
The constructor reads a wrapper construction length, requires a sequence tag, then loops through context-specific fields until the sequence end. Mechanism lists are sequences of OID elements, mechanism tokens and MICs are octet strings, and `ReqFlags` throws `NotImplementedException`. Serialization computes exact nested lengths, writes the outer tag/sequence, and emits only non-null optional fields.

## State, Dependencies, and Integration
Instances are mutable token DTOs. `GSSProvider` uses them to advertise mechanisms and process client SPNEGO init. `NTLMAuthenticationClient` uses them to wrap an NTLM negotiate message and to compute the mechanism-list bytes needed for MIC.

## Risks and Test Signals
`MechanismTypeList` is optional in the class but server logic assumes non-null/countable when accepting init tokens. Required flags are explicitly unsupported. Tests should cover empty lists, missing mechanism token, MIC round trips, long DER lengths, and parser behavior for unexpected tags or malformed nested sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit.cs -->
