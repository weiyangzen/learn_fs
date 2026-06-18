# sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go -->
## sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go

Purpose: validates the constraints and sticky-error behavior of `FakeSeeker`.

Important APIs and control flow: `TestFakeSeeker` verifies that real `io.ReadSeeker` inputs pass through unchanged, virtual seeking works before reads, reads from nonzero offsets fail, invalid whence and negative positions fail, reading from zero succeeds, and seeking after reading fails. `TestFakeSeekerError` reads to EOF and verifies subsequent read/seek return EOF.

State, dependencies, and integration: tests use `bytes.Buffer`, `bytes.Reader`, `io`, and testify. An interface assertion confirms `*FakeSeeker` implements `io.ReadSeeker`.

Risks and test signals: the tests clearly define the adapter's intentionally limited seek semantics. They do not test short reads with non-EOF errors or concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go -->
