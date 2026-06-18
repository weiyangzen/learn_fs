# sources/user-network-fs/libfuse/include/cuse_lowlevel.h

## Purpose
`cuse_lowlevel.h` declares the public low-level CUSE API for character devices in userspace. CUSE reuses FUSE low-level request/session machinery but presents a character-device operation surface rather than a filesystem tree.

## Important APIs, Types, and Functions
The header defaults `FUSE_USE_VERSION` to 29 if unset and includes `fuse_lowlevel.h`. `CUSE_UNRESTRICTED_IOCTL` is the only local flag. `struct cuse_info` contains desired device major/minor, device-info argument vector, and flags. `struct cuse_lowlevel_ops` contains callbacks for `init`, `init_done`, `destroy`, `open`, `read`, `write`, `flush`, `release`, `fsync`, `ioctl`, and `poll`; unlike FUSE low-level filesystem ops, these generally do not take inode numbers. Public constructors/runners are `cuse_lowlevel_new`, `cuse_lowlevel_setup`, `cuse_lowlevel_teardown`, and `cuse_lowlevel_main`.

## Control Flow
Applications fill `cuse_info` and `cuse_lowlevel_ops`, then call one of the setup/main helpers to create a `struct fuse_session` and enter normal FUSE session processing. The kernel routes character-device opens, reads, writes, ioctls, and poll events to the registered callbacks. `init_done` runs after initialization completes.

## State and Persistence
The header defines no state. Runtime state is held by the session created by the CUSE helpers and by application userdata. Device identity is controlled by major/minor and device info arguments; the actual character device lifetime is tied to setup/teardown.

## Dependencies and Integration Points
CUSE depends on low-level FUSE types (`fuse_req_t`, `struct fuse_file_info`, `struct fuse_conn_info`, `struct fuse_pollhandle`) and POSIX types for offsets and I/O vectors. It integrates with the same event-loop/session infrastructure used by low-level FUSE filesystems.

## Risks
The API is low-level: callback implementers must reply to requests correctly and manage unrestricted ioctl behavior carefully. If `CUSE_UNRESTRICTED_IOCTL` is set, ioctl argument handling can expose broader kernel/userspace ABI risk. Because the header defaults `FUSE_USE_VERSION`, including order can affect ABI selection if applications forget to define it explicitly.

## Test Signals
Compile a CUSE example such as `example/cusexmp.c`, create a device with specific dev info, and exercise open/read/write/ioctl/poll. ABI tests should include C++ inclusion through the `extern "C"` block and builds with explicit versus default `FUSE_USE_VERSION`.
