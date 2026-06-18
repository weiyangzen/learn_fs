# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenInitSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenInitSpec.groovy

Purpose: tests SPNEGO `NegTokenInit` ASN.1 parsing/writing. It reads fixture bytes for negotiate-token init messages and asserts mechanism OIDs, mechanism token payloads, and other negotiation fields, then validates serialization where covered.

State and persistence: fixture bytes loaded from test resources and transient ASN.1 token objects. Dependencies are SPNEGO token classes, buffer utilities, and OID/ASN.1 handling. Integration point is authentication negotiation before NTLM challenge/response. Risks covered include DER length/tag parsing, OID order, optional field handling, and mechanism-token preservation. Test signal is good for known SPNEGO handshakes.
