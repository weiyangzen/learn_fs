# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DFSTest.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DFSTest.groovy

Purpose: Spock research fixture for DFS path resolution through `Session.resolver`, `SmbPath`, `DFSReferralV34`, and `SMB2GetDFSReferralResponse`. Important flow: all concrete scenarios are currently commented out, but they document intended root referral, domain referral, root link, and interlink resolution flows using a stubbed `Connection`, `SMBClient`, `StubResponder`, `SMB2IoctlResponse`, tree connect/disconnect packets, and synchronous `DirectFuture`.

State and persistence: no active test state; dormant helpers would model transient connection/session state and referral responses only. Dependencies are SMBJ connection/auth/event/security classes and SMB DFS referral message encoders. Integration risk is that DFS resolver behavior can regress without this file failing because executable tests are disabled. Test signal is therefore weak: it is useful as design documentation, not coverage.
