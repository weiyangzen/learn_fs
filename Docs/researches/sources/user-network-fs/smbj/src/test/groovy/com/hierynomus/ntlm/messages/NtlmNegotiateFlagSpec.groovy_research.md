# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmNegotiateFlagSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmNegotiateFlagSpec.groovy

Purpose: parameterized Spock tests for NTLM negotiate flag bit handling. It verifies individual `NtlmNegotiateFlag` values are detected in raw integer flag words and that enum sets are serialized back into the expected flag values.

State and persistence: none. Dependencies are NTLM flag enums and enum-with-value utilities. Integration point is NTLM negotiate/challenge/authenticate message parsing and writing. Risks covered include bit position mistakes, high-bit signedness issues, and divergence between parse and encode paths. Test signal is focused on flags rather than full messages.
