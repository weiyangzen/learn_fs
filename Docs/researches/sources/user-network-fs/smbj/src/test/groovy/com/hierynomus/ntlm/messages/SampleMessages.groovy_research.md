# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/SampleMessages.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/SampleMessages.groovy

Purpose: shared Spock/Groovy fixture containing NTLM protocol sample data. It defines Windows version metadata, expected negotiate flag sets for NTLMv1, NTLMv1 with client challenge, and NTLMv2, plus byte arrays for sample challenge messages and response computations.

State and persistence: constant in-memory fixture fields only. Dependencies are `WindowsVersion`, `NtlmNegotiateFlag`, enum sets, and byte-array literals. Integration point is reused by NTLM message/function specs to keep protocol vectors consistent. Risks are fixture drift and accidental mutation because Groovy `def` fields can be mutable. Test signal is indirect: this file has no assertions but is critical for reproducible authentication tests.
