# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_i.hpp

## Purpose
`fuse_i.hpp` is the private internal header for the vendored FUSE implementation. It defines the simplified session shape and internal notification/request wiring shared by the loop, session, and low-level dispatch files.

## Important APIs, Types, and Functions
`struct fuse_session` contains callback pointers for receiving and processing buffers, a destroy callback, the low-level data pointer, atomic exit state, the active `/dev/fuse` fd, buffer size, and cloned read fds. `struct fuse_notify_req` models an intrusive pending-notify list with a unique id and reply callback. Internal declarations include `fuse_session_setup_read_fds`, `fuse_session_read_fd`, and `fuse_lowlevel_new_common`.

## Control Flow
The library collapses libfuse's former session/channel hierarchy for mergerfs' single-mount model. `fuse_session.cpp` fills and owns this structure, `fuse_loop.cpp` reads from either the main or cloned fds, and `fuse_lowlevel.cpp` installs receive/process callbacks and notification state.

## State and Persistence
Session state is in-memory and process-local. `exited` is atomic so signal handlers and worker threads can coordinate shutdown. `clone_fds` are owned by the session and closed when the session fd changes or the session is destroyed.

## Dependencies and Integration Points
The header includes public FUSE headers plus `fuse_msgbuf_t.h`, C++ `<atomic>`, and `<vector>`. It is a private bridge between high-level setup, low-level kernel protocol handling, signal handling, and the threaded loop.

## Risks
Because callback pointers are cast from `void *` in `fuse_session_new`, signatures must remain exactly compatible. Any future multi-mount support would require undoing the simplified single-session globals. Atomic exit protects the flag but not the rest of the session fields, so fd changes must remain lifecycle-bound.

## Test Signals
Build tests should catch signature drift. Runtime tests should cover single-thread shared-fd reads, multi-read-thread cloned-fd setup/fallback, signal-triggered exit, and session destroy after failed mount/setup.
