# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ProtocolNegotiatorTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ProtocolNegotiatorTest.java

Purpose: tests SMB protocol negotiation. It validates dialect selection, negotiate request/response handling, negotiated protocol fields, capabilities, signing/encryption requirements, and unsupported dialect/status outcomes.

State and persistence: transient negotiation inputs and resulting negotiated protocol object. Dependencies are SMB2 negotiate messages, dialect enums, config, security mode/capability fields, and JUnit/Mockito. Integration point is the first step of every SMB connection. Risks covered include choosing an unsupported dialect, misreading max read/write/transact sizes, mishandling server capabilities, and weak signing policy. Test signal is central for connection compatibility.
