# sources/user-network-fs/rclone/lib/readers/noseeker.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker.go -->
## sources/user-network-fs/rclone/lib/readers/noseeker.go

Purpose: adapts an `io.Reader` to an `io.ReadSeeker` whose `Seek` always fails. This can satisfy interfaces while explicitly preventing seeking.

Important APIs and control flow: `NoSeeker` embeds `io.Reader`. `Seek` ignores offset and whence and returns `(0, errCantSeek)`.

State, dependencies, and integration: state is the embedded reader. Dependencies are `errors` and `io`. It integrates with code paths that require a read seeker but can handle seek failures.

Risks and test signals: callers may treat `io.Seeker` support as a guarantee of usable seeking, so this adapter should only be used where explicit seek failure is accepted. The paired test verifies read delegation and seek error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker.go -->
