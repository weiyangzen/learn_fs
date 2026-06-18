# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/SmbConfigTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/SmbConfigTest.java

Purpose: tests `SmbConfig` builder validation. It verifies default config creation and asserts invalid combinations throw, especially requiring signing while disabling signing and disabling signing while allowing SMB 3.x dialects.

State and persistence: immutable config objects only. Dependencies are JUnit and SMBJ config/dialect/signing settings. Integration point is client construction and security policy enforcement. Risks covered include accepting insecure or contradictory configuration that would later fail negotiation or weaken session security. Test signal is small but important for early validation.
