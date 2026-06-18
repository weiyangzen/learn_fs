# sources/user-network-fs/rclone/lib/readers/fakeseeker.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker.go -->
## sources/user-network-fs/rclone/lib/readers/fakeseeker.go

Purpose: adapts a non-seekable `io.Reader` into an `io.ReadSeeker` for code that only needs to seek before reading, commonly to inspect or advertise a known length.

Important APIs and control flow: `NewFakeSeeker(in, length)` returns `in` unchanged if it already implements `io.ReadSeeker`; otherwise it returns `*FakeSeeker`. `Seek` supports standard whence values only before reading starts and records the virtual offset. `Read` fails if the first read is attempted from a nonzero offset, delegates to `in.Read`, marks the stream as read once bytes are returned, and stores the first read error in `readErr`; future `Read` or `Seek` return that stored error.

State, dependencies, and integration: state includes virtual `length`, `offset`, `read` flag, and sticky `readErr`. Dependencies are `errors`, `fmt`, and `io`. It integrates with APIs that require `io.ReadSeeker` but can tolerate only pre-read length seeking.

Risks and test signals: after EOF, all later operations return EOF. There is no synchronization. Seeking forward before reading makes the stream unreadable unless seeking back to zero. Tests cover pass-through, allowed seeks, invalid whence, negative positions, nonzero read failure, post-read seek failure, and sticky EOF.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker.go -->
