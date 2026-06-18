# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/MsDataTypesTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/MsDataTypesTest.java

Purpose: JUnit tests for Microsoft data type helpers. It verifies serialization/parsing behavior for small MS-DTYP primitives used by SMB protocol structures, such as UUID/GUID, file time, or numeric wrappers depending on implementation coverage.

State and persistence: in-memory values and buffers only. Dependencies are MS-DTYP classes and JUnit assertions. Integration point is protocol structure parsing throughout SMBJ. Risks covered include endian/layout mismatches and conversion errors in shared primitive types. Test signal is foundational but scoped to representative cases.
