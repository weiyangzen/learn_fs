# sources/user-network-fs/smbj/src/test/java/com/hierynomus/mserref/NtStatusTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/mserref/NtStatusTest.java

Purpose: parameterized tests for NT status severity classification. It checks selected `NtStatus` values report `STATUS_SEVERITY_SUCCESS` or `STATUS_SEVERITY_ERROR` as expected.

State and persistence: enum constants only. Dependencies are JUnit 5 parameterized tests and `NtStatus`. Integration point is error handling and exception mapping across SMB responses. Risks covered include incorrect severity-bit masking, which would misclassify protocol statuses. Test signal is small but useful for status helper correctness.
