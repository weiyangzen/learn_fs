<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/wait.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/record/wait.go

Purpose: recorder for asynchronous FUSE `Release` calls with optional timeout waiting.

Important APIs, types, and functions: `ReleaseWaiter` implements `fs.HandleReleaser` with `Release` and exposes `WaitForRelease`.

Control flow: lazy `init` creates a buffered channel once. `Release` copies and sanitizes the request, sends it, and closes the channel. `WaitForRelease` blocks forever or until a timeout.

State and persistence behavior: in-memory once/channel state only.

Dependencies and integration points: used by tests where release is not synchronous with client close.

Risks and test signals: repeated Release calls after channel close would panic, matching the assumption of one release per handle. Timeout behavior avoids relying on global test timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/wait.go -->
