# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmChallengeSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmChallengeSpec.groovy

Purpose: validates decoding of NTLM challenge messages supplied by `SampleMessages`. It constructs `NtlmChallenge`, reads byte arrays through the message API, and asserts fields for NTLMv1, NTLMv1 with client challenge/extended session security, and NTLMv2. Important checks include target name, negotiate flags, server challenge bytes, target info, and version data.

State and persistence: test data is held in the `SampleMessages` trait; parsing is per-test. Dependencies are NTLM message types and buffer utilities. Integration point is SPNEGO/NTLM authentication challenge handling. Risks covered include security-buffer offsets, negotiated flag sets, target-info AV pairs, and version decoding. Test signal is strong for protocol sample coverage.
