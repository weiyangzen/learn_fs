# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SMBSessionBuilderSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SMBSessionBuilderSpec.groovy

Purpose: tests session setup construction and authentication negotiation paths in `SMBSessionBuilder`. It uses stubbed connection/session setup responses and authenticators to verify selected authentication context, guest/anonymous flags, and session construction behavior around SMB2 session setup.

State and persistence: transient session-builder state, selected auth context, and response fields; no persistence. Dependencies are SMB session setup messages, auth interfaces, security providers, connection stubs, and Spock mocks. Integration point is login/authentication before share access. Risks covered include incorrect session flags, authenticator selection, and session-id propagation. Test signal is important because session establishment controls subsequent signing/encryption and permissions.
