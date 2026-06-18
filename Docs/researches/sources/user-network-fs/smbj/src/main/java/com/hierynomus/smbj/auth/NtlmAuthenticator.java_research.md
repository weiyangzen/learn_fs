# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmAuthenticator.java

Purpose: `NtlmAuthenticator` implements NTLMSSP over SPNEGO for SMB session setup.

Important APIs and control flow: after `init`, state starts at `NEGOTIATE`. First `authenticate` builds NTLM negotiate flags, serializes `NtlmNegotiate` into `NegTokenInit`, and moves to `AUTHENTICATE`. The next call parses `NegTokenTarg`, reads `NtlmChallenge`, intersects flags with server support, requires 128-bit encryption, computes NTLMv2 response and session key, optionally encrypts a random exported session key, calculates MIC when target-info flags require it, and returns `NtlmAuthenticate` in `NegTokenTarg`.

State, dependencies, and integration: it holds security provider, random, NTLM config, NTLMv2 functions, current flags, and the original negotiate message for MIC. It supports only exact `AuthenticationContext`, while `NtlmSealer` may wrap it.

Risks: stateful instances cannot be reused. Anonymous/guest flag handling is subtle. MIC and target-info behavior has TODOs. Tests should cover negotiate flag composition, challenge parsing, unsupported 128-bit failure, anonymous and guest paths, MIC calculation, session-key derivation, and state completion.
