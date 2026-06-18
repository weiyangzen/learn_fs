<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_pollhandle.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_pollhandle.h

Purpose: `fuse_pollhandle_t` records kernel poll handle state for readiness notifications.

Important fields: `kh` is the kernel handle to wake, and `se` points to the owning `fuse_session`.

State and integration: poll callbacks receive these handles and may later call notification functions such as `fuse_notify_poll` or `fuse_lowlevel_notify_poll`. The session pointer ties notifications to the correct mount.

Risks and test signals: handles are only valid until destroyed; stale handles can notify the wrong or freed session. Tests should cover poll callback scheduling, destroy behavior, and notification after release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_pollhandle.h -->
