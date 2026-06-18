# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenTargSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenTargSpec.groovy

Purpose: tests SPNEGO `NegTokenTarg` parsing with an embedded NTLM challenge. It loads `spnego/negTokenTarg_ntlmchallenge`, reads the token from a little-endian plain buffer, extracts the response token, and feeds it to `NtlmChallenge` for validation.

State and persistence: resource bytes only. Dependencies are `NegTokenTarg`, `NtlmChallenge`, and protocol buffers. Integration point is the handoff from SPNEGO target token parsing to NTLM challenge decoding. Risks covered include ASN.1 response-token extraction, nested token boundaries, and compatibility with NTLM challenge parser. Test signal is focused on one real fixture.
