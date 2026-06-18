# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/functions/NtlmFunctionsSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/functions/NtlmFunctionsSpec.groovy

Purpose: cryptographic test vectors for NTLMv1/v2 helper functions across multiple security providers. Important types include `NtlmV1Functions`, `NtlmV2Functions`, `NtlmFunctions`, `TargetInfo`, `NtlmChallenge`, `PredictableRandom`, `JceSecurityProvider`, `BCSecurityProvider`, and Bouncy Castle provider. Control flow checks LMOWFv1, RC4 encryption, MS-NLMP NTLMv1 examples, NTLMv2 hash/response temp/computed response examples, deterministic client challenge bytes, and target-info parsing.

State and persistence: a static predictable random source supplies deterministic bytes; no persistence. Dependencies are crypto providers and official protocol example data. Integration point is authentication, signing/sealing key material, and NTLM response generation. Risks are high: provider-specific digest/cipher behavior and deterministic test vectors must remain exact. Test signal is strong for spec examples, limited to known inputs.
