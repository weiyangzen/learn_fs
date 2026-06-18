# sources/user-network-fs/rclone/lib/readers/noseeker_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker_test.go -->
## sources/user-network-fs/rclone/lib/readers/noseeker_test.go

Purpose: tests `NoSeeker`'s read delegation and intentional seek failure.

Important APIs and control flow: `TestNoSeeker` reads four bytes from a `bytes.Buffer` through `NoSeeker` and checks the bytes, then calls `Seek` and expects `errCantSeek`. Interface assertions confirm `NoSeeker` satisfies both `io.Reader` and `io.Seeker`.

State, dependencies, and integration: dependencies are `bytes`, `io`, `testing`, and testify.

Risks and test signals: this is a direct smoke test. It does not cover nil embedded readers or caller behavior after a failed seek.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker_test.go -->
