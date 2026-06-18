# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/SIDTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/SIDTest.java

Purpose: tests Windows SID string/binary conversion. It asserts `SID.fromString` and serialization/parsing behavior for known SID forms, including identifier authority and sub-authority components.

State and persistence: immutable SID values and transient buffers. Dependencies are `SID`, JUnit, and buffer utilities. Integration point is security descriptor parsing, ACL entries, and access-control display. Risks covered include authority width, sub-authority endian handling, invalid string forms, and equality semantics. Test signal is targeted and important for security descriptor correctness.
