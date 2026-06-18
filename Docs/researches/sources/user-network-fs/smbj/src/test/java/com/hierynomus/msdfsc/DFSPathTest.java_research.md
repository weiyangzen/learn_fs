# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/DFSPathTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/DFSPathTest.java

Purpose: JUnit tests for `DFSPath` parsing and path matching. It constructs DFS paths from UNC-style strings and validates host/share/path components, root/link style interpretation, and matching behavior used by referral caches.

State and persistence: immutable path values only. Dependencies are JUnit assertions and DFS path model classes. Integration point is DFS referral lookup and path-prefix comparison. Risks covered include separator handling, case/path component boundaries, and incorrect root/share extraction. Test signal is focused on DFS path semantics independent of network behavior.
