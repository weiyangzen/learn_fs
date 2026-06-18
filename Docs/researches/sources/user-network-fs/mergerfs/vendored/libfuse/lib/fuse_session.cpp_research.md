# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_session.cpp

## Purpose
`fuse_session.cpp` implements the simplified single-mount session lifecycle and fd management.

## Important APIs, Types, and Functions
It defines `fuse_session_new`, `fuse_session_destroy`, `fuse_session_reset`, `fuse_session_exited`, `fuse_session_exit`, `fuse_session_data`, `fuse_session_clearfd`, `fuse_session_setfd`, `fuse_session_setup_read_fds`, `fuse_session_read_fd`, `fuse_session_setbufsize`, `fuse_session_fd`, and `fuse_session_bufsize`. Internal helpers clone `/dev/fuse` fds via `FUSE_DEV_IOC_CLONE` and close clone fds.

## Control Flow
`fuse_session_new` allocates a C++ `fuse_session`, stores callbacks and low-level data, and initializes fd to `-1`. Destroy invokes the low-level destroy callback, closes clone fds and the main fd, then deletes the session. Multi-read setup attempts to open `/dev/fuse` and clone the main fd for each read worker beyond the first; on any clone failure it closes all clones, logs a warning, and falls back to the shared fd.

## State and Persistence
The session owns the main fd, cloned fds, buffer size, callback pointers, low-level data pointer, and atomic exit flag. State is in-memory and tied to mount lifetime.

## Dependencies and Integration Points
It depends on `fuse_i.hpp`, kernel ioctl constants, syslog, and POSIX fd APIs. `helper.cpp`/`fuse.cpp` set fd and bufsize; `fuse_loop.cpp` queries read fds; signal handling toggles exit state.

## Risks
Fd ownership is delicate: `fuse_session_clearfd` transfers the main fd to unmount code and closes clones. Cloned-fd support depends on kernel support for `FUSE_DEV_IOC_CLONE`. Callback casts from `void *` require exact function signatures.

## Test Signals
Test session create/destroy, setfd replacing clones, clearfd transfer, clone success/failure fallback, multiple read thread fd selection, signal/session exit, and destroy after partial setup failure.
